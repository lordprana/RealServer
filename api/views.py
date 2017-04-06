from django.shortcuts import render
from rest_framework.authtoken.models import Token
from api.auth import custom_authenticate
from api.tasks import notifyUserPassedOn, notifyUpcomingDate
from api import hardcoded_dates
from api.models import User, BlockedReports, Gender, Status, SexualPreference, FCMDevice
from api.fake_user import generate_fake_user
from api.hardcoded_dates import getHardcodedDates
from matchmaking import views as matchmaking
from matchmaking.models import Date, DateStatus
from api.notifications import sendMatchNotification, sendLikeNotification
from api.default_radius_by_city import DEFAULT_RADIUS
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from  RealServer.tools import nextDayOfWeekToDatetime, cropImage, cropImageToSquare, cropImageByAspectRatio, \
    cropImageByAspectRatioAndCoordinates, convertLocalTimeToUTC
from RealServer.aws import s3_generate_presigned_post, s3_delete_file
from django.db import transaction
from django.db.models import Q
from PIL import Image
import json
import re
import os
import datetime
import urllib
import boto3
import random
import string
import os
import geocoder
import pytz
from pytz import timezone as pytz_timezone
from RealServer.settings import MAPBOX_API_KEY, FAKE_USERS
from StringIO import StringIO
import requests
from RealServer import facebook
# Create your views here.

@csrf_exempt
@custom_authenticate
def users(request, user):
    if request.method == 'POST':
        token = Token.objects.get(user=user)
        if user.status == Status.FINISHED_PROFILE.value or user.status == Status.INACTIVE.value:
            user.status = Status.FINISHED_PROFILE.value
            response_dict = {
                'fb_user_id' : user.fb_user_id,
                'real_auth_token': token.key,
                'status': user.status
            }
            user.save()
            return  JsonResponse(response_dict)

        user.status = Status.NEW_USER.value
        response_dict = {
                'fb_user_id' : user.fb_user_id,
                'real_auth_token': token.key,
                'status': user.status
            }

        json_data = json.loads(request.body)
        user.timezone = json_data.get('timezone', None)
        if not user.timezone:
            return HttpResponse(status=400)

        user_json = facebook.getUserInfo(user)
        if user_json.get('gender', None) == 'male':
            user.gender = Gender.MAN.value
        elif user_json.get('gender', None) == 'female':
            user.gender = Gender.WOMAN.value

        interested_in = user_json.get('interested_in', None)
        if interested_in:
            if len(interested_in) > 1:
                user.interested_in = SexualPreference.BISEXUAL.value
            elif interested_in[0] == 'male':
                user.interested_in = SexualPreference.MEN.value
            elif interested_in[0] == 'female':
                user.interested_in = SexualPreference.WOMEN.value
        user.first_name = user_json.get('first_name', None)
        user.last_name = user_json.get('last_name', None)

        # Parse json for education and occupation
        user.education = user_json.get('education', None)
        if user.education:
            try:
                user.education = user.education[-1]['school']['name']
            except:
                user.education = None

        user.occupation = user_json.get('work', None)
        if user.occupation:
            try:
                user.occupation = user.occupation[0]['position']['name']
            except:
                user.occupation = None
        # Convert birthday to age
        try:
            bd = datetime.datetime.strptime(user_json['birthday'], '%m/%d/%Y')
        except ValueError:
            try:
                bd = datetime.datetime.strptime(user_json['birthday'], '%Y')
            except:
                bd = None
        except KeyError:
            bd = None
        if bd:
            today = timezone.now()
            user.age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

        # Set age preferences depending on user's age
        if user.age:
            user.min_age_preference = user.age - 10
            user.max_age_preference = user.age + 10
            if user.min_age_preference < 18:
                user.min_age_preference = 18
            if user.max_age_preference > 99:
                user.max_age_preference = 99
        else:
            user.age = 21
            user.min_age_preference = 18
            user.max_age_preference = 31

        # Save pictures to S3. Images come in square and portrait flavors
        original_user_picture = facebook.getUserProfilePicture(user)

        if not original_user_picture:
            return HttpResponse(status=400)
        # TODO resize picture for optimal performance
        file_jpgdata = StringIO(original_user_picture)
        image = Image.open(file_jpgdata)
        square_user_picture = cropImageToSquare(image)
        request_json = json.loads(s3_generate_presigned_post('.jpg', user))
        # Save Pillow image to StringIO to send in post request
        img_io = StringIO()
        square_user_picture.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        files = {'file': img_io.read()}
        r = requests.post(request_json['data']['url'], data=request_json['data']['fields'], files=files)
        if r.status_code == 204:
            user.picture1_square_url = request_json['url']
        else:
            return HttpResponse(status=400)

        aspect_width = 205
        aspect_height = 363
        file_jpgdata = StringIO(original_user_picture)
        image = Image.open(file_jpgdata)
        portrait_user_picture = cropImageByAspectRatio(image, aspect_width, aspect_height)
        request_json = json.loads(s3_generate_presigned_post('.jpg', user))
        # Save Pillow image to StringIO to send in post request
        img_io = StringIO()
        portrait_user_picture.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        files = {'file': img_io.read()}
        r = requests.post(request_json['data']['url'], data=request_json['data']['fields'], files=files)
        if r.status_code == 204:
            user.picture1_portrait_url = request_json['url']
        else:
            return HttpResponse(status=400)

        user.save()
        return JsonResponse(response_dict)
    else:
        return HttpResponse(status=400)


@csrf_exempt
@custom_authenticate
def user(request,user):
    if request.method == 'PATCH':
        json_data = json.loads(request.body)
        temp_user = User.objects.get(pk=user.pk)
        for key, value in json_data.iteritems():
            if key == 'real_auth_token':
                continue
            # Education is provided in the last step of setting up a profile, so if it's here, we know to change the
            # user status.
            elif key == 'education':
                user.status = Status.FINISHED_PROFILE.value
            elif re.search('^picture', key) and re.search('_url$', key):
                pass
                """
                picture_url = value
                picture_startx = json_data[key[:8]+'_startx']
                picture_endx = json_data[key[:8] + '_endx']
                picture_starty = json_data[key[:8] + '_starty']
                picture_endy = json_data[key[:8] + '_endy']
                aspect_width = 205
                aspect_height = 365
                picture = urllib.urlopen(picture_url)

                original_picture = picture.read()
                f = open(settings.MEDIA_ROOT + user.fb_user_id + '/' + key[:8] + '_original.jpg', 'w')
                f.write(original_picture)

                square_picture = cropImage(original_picture, picture_startx, picture_starty, picture_endx, picture_endy)
                f = open(settings.MEDIA_ROOT + user.fb_user_id + '/' +  key[:8] + '_square.jpg', 'w')
                f.write(square_picture)
                setattr(user, key[:8] + '_square_url', request.META['HTTP_HOST'] + '/' + settings.MEDIA_URL + \
                                                       user.fb_user_id + '/' + key[:8] + '_square.jpg')

                portrait_picture = cropImageByAspectRatioAndCoordinates(original_picture, picture_startx, picture_starty,
                                                                        picture_endx, picture_endy,
                                                                        aspect_width, aspect_height)
                f = open(settings.MEDIA_ROOT + user.fb_user_id + '/' + key[:8] + '_portrait.jpg', 'w')
                f.write(portrait_picture)
                setattr(user, key[:8] + '_portrait_url', request.META['HTTP_HOST'] + '/' + settings.MEDIA_URL + \
                        user.fb_user_id + '/' + key[:8] + '_portrait.jpg')
                """
            elif key == 'latitude':
                if not user.registration_city:
                    try:
                        latlng = [json_data['latitude'], json_data['longitude']]
                    except:
                        return HttpResponse(status=400)
                    g = geocoder.mapbox(latlng, method='reverse', key=MAPBOX_API_KEY)
                    if g.status_code == 200:
                        if g.city and g.state:
                            user.registration_city = g.city
                            user.registration_state = g.state
                            radius = DEFAULT_RADIUS.get(user.registration_city + ', ' + user.registration_state, None)
                            if radius:
                                user.search_radius = radius
            setattr(user, key, value)
        user.save()
        # Delete unused pictures
        for i in range(1, 7):
            seen_square = False
            seen_portrait = False
            for j in range(1, 7):
                if getattr(temp_user, 'picture'+str(i)+'_square_url') == getattr(user, 'picture'+str(j)+'_square_url'):
                    seen_square = True
                if getattr(temp_user, 'picture' + str(i) + '_portrait_url') == getattr(user, 'picture' + str(j) + '_portrait_url'):
                    seen_portrait = True
            if not seen_square and getattr(temp_user, 'picture'+str(i)+'_square_url') != None:
                s3_delete_file(getattr(temp_user, 'picture'+str(i)+'_square_url'))
            if not seen_portrait and getattr(temp_user, 'picture'+str(i)+'_portrait_url') != None:
                s3_delete_file(getattr(temp_user, 'picture'+str(i)+'_portrait_url'))


        return HttpResponse(status=200)

    elif request.method == 'GET':
        details = {
            'interested_in': user.interested_in,
            'occupation': user.occupation,
            'name': user.first_name,
            'age': user.age,
            'gender': user.gender,
            'education': user.education,
            'about': user.about,
            'picture1_square_url': user.picture1_square_url,
            'picture1_portrait_url': user.picture1_portrait_url,
            'picture2_square_url': user.picture2_square_url,
            'picture2_portrait_url': user.picture2_portrait_url,
            'picture3_square_url': user.picture3_square_url,
            'picture3_portrait_url': user.picture3_portrait_url,
            'picture4_square_url': user.picture4_square_url,
            'picture4_portrait_url': user.picture4_portrait_url,
            'picture5_square_url': user.picture5_square_url,
            'picture5_portrait_url': user.picture5_portrait_url,
            'picture6_square_url': user.picture6_square_url,
            'picture6_portrait_url': user.picture6_portrait_url,
        }
        return JsonResponse(details)

@csrf_exempt
@custom_authenticate
def settings(request, user):
    settings_json = {
        'search_radius': user.search_radius,
        'min_age_preference': user.min_age_preference,
        'max_age_preference': user.max_age_preference,
        'max_price': user.max_price,
        'new_likes_notification': user.new_likes_notification,
        'new_matches_notification': user.new_matches_notification,
        'new_messages_notification': user.new_messages_notification,
        'upcoming_dates_notification': user.upcoming_dates_notification,
        'pass_notification': user.pass_notification
    }
    return JsonResponse(settings_json)

@csrf_exempt
@custom_authenticate
def date(request, user, date_id=None):
    if request.method == 'GET':
        if date_id:
            try:
                date = Date.objects.get(pk=date_id)
            except:
                return HttpResponse(status=404)
            return JsonResponse(matchmaking.convertDateToJson(user, date), safe=False)
        else:
            day = request.GET.get('day', None)

            # Used for testing
            if request.GET.get('hardcoded', None):
                return getHardcodedDates(user, day)
            # Used for testing
            if FAKE_USERS and not user.is_fake_user:
                if user.interested_in == SexualPreference.WOMEN.value:
                    generate_fake_user(SexualPreference.WOMEN.value, request.GET.get('latitude', None),
                                       request.GET.get('longitude', None))
                elif user.interested_in == SexualPreference.MEN.value:
                    generate_fake_user(SexualPreference.MEN.value, request.GET.get('latitude', None),
                                       request.GET.get('longitude', None))
                elif user.interested_in == SexualPreference.BISEXUAL.value:
                    if random.randint(0, 1):
                        generate_fake_user(SexualPreference.MEN.value, request.GET.get('latitude', None),
                                           request.GET.get('longitude', None))
                    else:
                        generate_fake_user(SexualPreference.WOMEN.value, request.GET.get('latitude', None),
                                           request.GET.get('longitude', None))


            return matchmaking.date(request, user, day)

    if request.method == 'PATCH':
        date = Date.objects.get(pk=date_id)
        request_json = json.loads(request.body)

        # Which user is request coming from
        if user == date.user1:
            request_user = 'user1'
            match_user = 'user2'
        else:
            request_user = 'user2'
            match_user = 'user1'

        status = request_json.get('status', None)
        inspected_match = request_json.get('inspected_match', None)
        if not status and not inspected_match:
            return HttpResponse(status=400)
        if status:
            setattr(date, request_user+'_likes', status)
            match_user_object = getattr(date, match_user)
            if status == DateStatus.LIKES.value:
                match_user_object.num_times_liked = match_user_object.num_times_liked + 1
                match_user_object.save()
            # If both users like each other, then set the date to expire at the last minute on the day of the date
            if status == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.LIKES.value:
                date.expires_at = datetime.datetime.combine(date.date_of_date, datetime.time(hour=23, minute=59,
                                                                                             second=0, microsecond=0,
                                                                                             tzinfo=None))
                local_expires_at = convertLocalTimeToUTC(date.expires_at, user.timezone)
                date.expires_at = local_expires_at
                sendMatchNotification(getattr(date, request_user), getattr(date, match_user), date)
                datetime_of_date = pytz_timezone(user.timezone).localize(datetime.datetime.combine(date.date_of_date, date.start_time))
                upcoming_date_reminder_time = datetime_of_date - datetime.timedelta(days=1)
                if upcoming_date_reminder_time > timezone.now():
                    transaction.on_commit(lambda: notifyUpcomingDate.apply_async((getattr(date, request_user).pk,
                                                                                  getattr(date, match_user).pk,
                                                                                  date.pk),
                                                                                 eta=upcoming_date_reminder_time))
            # If it's a like, but other user has passed notify user after two hours that they've been passed on
            elif status == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.PASS.value:
                datetime_of_date = pytz_timezone(user.timezone).localize(datetime.datetime.combine(date.date_of_date, date.start_time))
                if (datetime_of_date - datetime.timedelta(minutes=30)) < timezone.now() + datetime.timedelta(hours=24):
                    date.expires_at = datetime_of_date - datetime.timedelta(minutes=30)
                else:
                    date.expires_at = timezone.now() + datetime.timedelta(hours=24)
                transaction.on_commit(lambda: notifyUserPassedOn.apply_async((getattr(date, match_user).pk,
                                                                              getattr(date, request_user).pk,
                                                                             date.pk),
                                                                             countdown=60*60*2))
            # If it's a like and the other user hasn't responded, add 24 hours to the expires_at time
            elif status == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.UNDECIDED.value:
                datetime_of_date = pytz_timezone(user.timezone).localize(datetime.datetime.combine(date.date_of_date, date.start_time))
                if (datetime_of_date - datetime.timedelta(minutes=30)) < timezone.now() + datetime.timedelta(hours=24):
                    date.expires_at = datetime_of_date - datetime.timedelta(minutes=30)
                else:
                    date.expires_at = timezone.now() + datetime.timedelta(hours=24)
                sendLikeNotification(getattr(date, request_user), getattr(date, match_user), date)
            elif status == DateStatus.PASS.value and getattr(date, match_user+'_likes') == DateStatus.LIKES.value:
                # Notify user after two hours that they've been passed on
                transaction.on_commit(lambda: notifyUserPassedOn.apply_async((getattr(date, request_user).pk,
                                                                             getattr(date, match_user).pk,
                                                                             date.pk),
                                                                             countdown=60*60*2))
            elif status == DateStatus.PASS.value and getattr(date, match_user + '_likes') == DateStatus.UNDECIDED.value:
                getattr(date, request_user).passed_matches.add(getattr(date, match_user))
            elif status == DateStatus.PASS.value and getattr(date,
                                                                                 match_user + '_likes') == DateStatus.PASS.value:
                getattr(date, request_user).passed_matches.add(getattr(date, match_user))

        if inspected_match:
            date.inspected_match = inspected_match

        date.save()
        return HttpResponse(status=200)

@csrf_exempt
@custom_authenticate
def unmatch(request, user, date_id):
    date = Date.objects.get(pk=date_id)
    date.expires_at = date.original_expires_at
    date.user1_likes = DateStatus.PASS.value
    date.user2_likes = DateStatus.PASS.value
    user1 = date.user1
    user2 = date.user2
    date.save()
    user1.passed_matches.add(user2)
    return HttpResponse(status=200)

@csrf_exempt
@custom_authenticate
def logout(request, user):
    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=user.pk)
        user.status = Status.INACTIVE.value
        user.save()
    return HttpResponse(status=200)

@csrf_exempt
@custom_authenticate
def report_and_block(request, user):
    if request.method == 'POST':
        try:
            request_json = json.loads(request.body)
            blocked_user = User.objects.get(pk=request_json['blocked_user_id'])

            date = Date.objects.get(pk=request_json['date_id'])
            date.user1_likes = DateStatus.PASS.value
            date.user2_likes = DateStatus.PASS.value
            date.expires_at = date.original_expires_at
            date.save()

            user.passed_matches.add(blocked_user)
            blocked_user.passed_matches.add(user)
            user.save()
            blocked_user.save()

            BlockedReports.objects.create(blocking_user=user, blocked_user=blocked_user, associated_date=date,
                                          report_content=request_json['report_content'])
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=400)

@csrf_exempt
@custom_authenticate
def get_time_preferences(request, user):
    time_preferences = {
        'sun_start_time': user.sun_start_time,
        'sun_end_time': user.sun_end_time,
        'mon_start_time': user.mon_start_time,
        'mon_end_time': user.mon_end_time,
        'tue_start_time': user.tue_start_time,
        'tue_end_time': user.tue_end_time,
        'wed_start_time': user.wed_start_time,
        'wed_end_time': user.wed_end_time,
        'thur_start_time': user.thur_start_time,
        'thur_end_time': user.thur_end_time,
        'fri_start_time': user.fri_start_time,
        'fri_end_time': user.fri_end_time,
        'sat_start_time': user.sat_start_time,
        'sat_end_time': user.sat_end_time,
    }
    return JsonResponse(time_preferences)

@csrf_exempt
@custom_authenticate
def get_place_preferences(request, user):
    place_preferences = {
        'likes_drinks': user.likes_drinks,
        'likes_food': user.likes_food,
        'likes_coffee': user.likes_coffee,
        'likes_parks': user.likes_parks,
        'likes_museums': user.likes_museums,
        'likes_fun': user.likes_fun
    }
    return JsonResponse(place_preferences)

@csrf_exempt
@custom_authenticate
def sign_s3(request, user):
  file_type = request.GET.get('file_type')
  json_response = json.loads(s3_generate_presigned_post(file_type, user))
  return JsonResponse(json_response, safe=False)

@csrf_exempt
@custom_authenticate
def past_dates(request, user):
    user_tz_now = timezone.now().astimezone(pytz_timezone(user.timezone))
    past_dates = Date.objects.filter(user1_likes=DateStatus.LIKES.value, user2_likes=DateStatus.LIKES.value,
                                     date_of_date__lt=user_tz_now.date()).order_by('-date_of_date')
    past_dates = past_dates.filter(Q(user1=user) | Q(user2=user))
    dates_json = []
    for d in past_dates:
        dates_json.append(matchmaking.convertDateToJson(user, d))
    return JsonResponse(dates_json, safe=False)

@csrf_exempt
@custom_authenticate
def register_fcm_device(request, user):
    try:
        json_data = json.loads(request.body)
    except:
        return HttpResponse(status=400)
    registration_token = json_data.get('registration_token', None)
    if not registration_token:
        return HttpResponse(status=400)
    FCMDevice.objects.get_or_create(registration_token=registration_token, user=user)
    return HttpResponse(status=200)

@csrf_exempt
def fake_users(request):
    # Find fake users who have upcoming dates with real users
    fake_users = User.objects.filter(
        (Q(sun_date__user1__is_fake_user=False) & Q(sun_date__user2__is_fake_user=True) & Q(sun_date__expires_at__gt=timezone.now())) |
        (Q(sun_date__user1__is_fake_user=True) & Q(sun_date__user2__is_fake_user=False) & Q(sun_date__expires_at__gt=timezone.now())) |
        (Q(mon_date__user1__is_fake_user=False) & Q(mon_date__user2__is_fake_user=True) & Q(mon_date__expires_at__gt=timezone.now())) |
        (Q(mon_date__user1__is_fake_user=True) & Q(mon_date__user2__is_fake_user=False) & Q(mon_date__expires_at__gt=timezone.now())) |
        (Q(tue_date__user1__is_fake_user=False) & Q(tue_date__user2__is_fake_user=True) & Q(tue_date__expires_at__gt=timezone.now())) |
        (Q(tue_date__user1__is_fake_user=True) & Q(tue_date__user2__is_fake_user=False) & Q(tue_date__expires_at__gt=timezone.now())) |
        (Q(wed_date__user1__is_fake_user=False) & Q(wed_date__user2__is_fake_user=True) & Q(wed_date__expires_at__gt=timezone.now())) |
        (Q(wed_date__user1__is_fake_user=True) & Q(wed_date__user2__is_fake_user=False) & Q(wed_date__expires_at__gt=timezone.now())) |
        (Q(thur_date__user1__is_fake_user=False) & Q(thur_date__user2__is_fake_user=True) & Q(thur_date__expires_at__gt=timezone.now())) |
        (Q(thur_date__user1__is_fake_user=True) & Q(thur_date__user2__is_fake_user=False) & Q(thur_date__expires_at__gt=timezone.now())) |
        (Q(fri_date__user1__is_fake_user=False) & Q(fri_date__user2__is_fake_user=True) & Q(fri_date__expires_at__gt=timezone.now())) |
        (Q(fri_date__user1__is_fake_user=True) & Q(fri_date__user2__is_fake_user=False) & Q(fri_date__expires_at__gt=timezone.now())) |
        (Q(sat_date__user1__is_fake_user=False) & Q(sat_date__user2__is_fake_user=True) & Q(sat_date__expires_at__gt=timezone.now())) |
        (Q(sat_date__user1__is_fake_user=True) & Q(sat_date__user2__is_fake_user=False) & Q(sat_date__expires_at__gt=timezone.now()))
    ).filter(is_fake_user=True).order_by('first_name')
    fake_user_json = []
    for user in fake_users:
        user_json = {
            'fb_user_id': user.pk,
            'first_name': user.first_name
        }
        fake_user_json.append(user_json)
    return JsonResponse(fake_user_json, safe=False)


