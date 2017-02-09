from django.shortcuts import render
from rest_framework.authtoken.models import Token
from api.auth import custom_authenticate
from api.tasks import notifyUserPassedOn
from api import hardcoded_dates
from api.models import User, BlockedReports, Gender, Status, SexualPreference, FCMDevice
from matchmaking import views as matchmaking
from matchmaking.models import Date, DateStatus
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from  RealServer.tools import nextDayOfWeekToDatetime, cropImage, cropImageToSquare, cropImageByAspectRatio, cropImageByAspectRatioAndCoordinates
from RealServer.aws import s3_generate_presigned_post, s3_delete_file
from django.db import transaction
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
from RealServer import settings
from StringIO import StringIO
import requests
from RealServer import facebook
# Create your views here.

@csrf_exempt
@custom_authenticate
def users(request, user):
    if request.method == 'POST':
        token = Token.objects.get(user=user)
        if user.status == Status.FINISHED_PROFILE.value or user.status == Status.INACTIVE:
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

        # Save pictures to S3. Images come in original, square, and portrait flavors
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
        aspect_height = 365
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
                # Check to make sure image is not used at all before deleting
                picture_exists = False
                for key2, value2 in json_data.iteritems():
                    if re.search('^picture', key2) and re.search('_url$', key2):
                        if key != key2 and getattr(temp_user, key2) == value and value != None:
                            picture_exists = True
                if not picture_exists and getattr(user, key):
                    s3_delete_file(getattr(user, key))
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
            elif re.match('^picture', key) and not re.match('_url$', key):
                pass
            setattr(user, key, value)
        user.save()
        return HttpResponse(status=200)

    elif request.method == 'GET':
        details = {
            'interested_in': user.interested_in,
            'occupation': user.occupation,
            'name': user.first_name,
            'age': user.age,
            'gender': user.gender,
            'education': user.education,
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
def date(request, user, date_id=None):
    if request.method == 'GET':
        day = request.GET.get('day', None)

        # Used for testing
        if request.GET.get('hardcoded', None):
            return JsonResponse(hardcoded_dates.dates[day])

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

        setattr(date, request_user+'_likes', request_json['status'])
        # If both users like each other, then set the date to expire at the last minute on the day of the date
        if request_json['status'] == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.LIKES.value:
            date.expires_at = nextDayOfWeekToDatetime(date.expires_at, date.day)
            date.expires_at = date.expires_at.replace(hour=23,minute=59, second=0, microsecond=0)
            #TODO: Send notification to match_user
        # If it's a like, but other user has passed notify user after two hours that they've been passed on
        elif request_json['status'] == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.PASS.value:
            date.expires_at = timezone.now() + datetime.timedelta(hours=24)
            transaction.on_commit(lambda: notifyUserPassedOn.apply_async((getattr(date, request_user).pk,
                                                                          getattr(date, match_user).pk,
                                                                         date.pk),
                                                                         countdown=60*60*2))
        # If it's a like and the other user hasn't responded, add 24 hours to the expires_at time
        elif request_json['status'] == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.UNDECIDED.value:
            date.expires_at = timezone.now() + datetime.timedelta(hours=24)
            # TODO: Send notification to match user
        elif request_json['status'] == DateStatus.PASS.value and getattr(date, match_user+'_likes') == DateStatus.LIKES.value:
            # Notify user after two hours that they've been passed on
            transaction.on_commit(lambda: notifyUserPassedOn.apply_async((getattr(date, match_user).pk,
                                                                         getattr(date, request_user).pk,
                                                                         date.pk),
                                                                         countdown=60*60*2))
        elif request_json['status'] == DateStatus.PASS.value and getattr(date, match_user + '_likes') == DateStatus.UNDECIDED.value:
            getattr(date, request_user).passed_matches.add(getattr(date, match_user))
        elif request_json['status'] == DateStatus.PASS.value and getattr(date,
                                                                             match_user + '_likes') == DateStatus.PASS.value:
            getattr(date, request_user).passed_matches.add(getattr(date, match_user))
        date.save()
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
            date.expires_at = timezone.now() - datetime.timedelta(days=1)
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
# TODO test this
def sign_s3(request, user):
  file_type = request.GET.get('file_type')
  json_response = json.loads(s3_generate_presigned_post(file_type, user))
  return JsonResponse(json_response, safe=False)

@csrf_exempt
@custom_authenticate
def past_dates(request, user):
    past_dates = Date.objects.filter(user1_likes=DateStatus.LIKES.value, user2_likes=DateStatus.LIKES.value,
                                     date_of_date__lt=timezone.now().date()).order_by('-date_of_date')
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



