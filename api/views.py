from django.shortcuts import render
from rest_framework.authtoken.models import Token
from api.auth import custom_authenticate
from api.tasks import notifyUserPassedOn
from api import hardcoded_dates
from api.models import User, BlockedReports, Gender
from matchmaking import views as matchmaking
from matchmaking.models import Date, DateStatus
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from  RealServer.tools import nextDayOfWeekToDatetime, cropImage, cropImageToSquare, cropImageByAspectRatio, cropImageByAspectRatioAndCoordinates
from django.db import transaction
import json
import re
import os
import datetime
import urllib
from RealServer import facebook
# Create your views here.

@csrf_exempt
@custom_authenticate
def users(request, user):
    if request.method == 'POST':
        token = Token.objects.get(user=user)
        response_dict = {
            'fb_user_id' : user.fb_user_id,
            'real_auth_token': token.key,
            'status': 'profile_incomplete'
        }
        #TODO test this once we have full permissions from users
        user_json = facebook.getUserInfo(user)
        user.education = user_json.get('education', None)
        if user_json.get('gender', None) == 'male':
            user.gender = Gender.MAN.value
        elif user_json.get('gender', None) == 'female':
            user.gender = Gender.WOMAN.value
        user.interested_in = user_json.get('interested_in', None)
        user.name = user_json.get('name', None)
        user.occupation = user_json.get('work', None)

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

        # Save pictures to disk. Images come in original, square, and portrait flavors
        original_user_picture = facebook.getUserProfilePicture(user)
        if not original_user_picture:
            return HttpResponse(status=400)
        # TODO resize picture for optimal performance
        if not os.path.exists(settings.MEDIA_ROOT + user.fb_user_id):
            os.makedirs(settings.MEDIA_ROOT + user.fb_user_id)
        f = open(settings.MEDIA_ROOT + user.fb_user_id + '/' + 'picture1_original.jpg', 'w')
        f.write(original_user_picture)

        square_user_picture = cropImageToSquare(original_user_picture)
        square_user_picture.save(settings.MEDIA_ROOT + user.fb_user_id + '/' + 'picture1_square.jpg')
        #f = open(settings.MEDIA_ROOT + user.fb_user_id + '/' + 'picture1_square.jpg', 'w')
        #f.write(square_user_picture)
        user.picture1_square_url = request.META['HTTP_HOST']+ '/' + settings.MEDIA_URL + user.fb_user_id + '/picture1_square.jpg'

        aspect_width = 205
        aspect_height = 365
        portrait_user_picture = cropImageByAspectRatio(original_user_picture, aspect_width, aspect_height)
        #f = open(settings.MEDIA_ROOT + user.fb_user_id + '/' + 'picture1_portrait.jpg', 'w')
        #f.write(portrait_user_picture)
        portrait_user_picture.save(settings.MEDIA_ROOT + user.fb_user_id + '/' + 'picture1_portrait.jpg')
        user.picture1_portrait_url = request.META['HTTP_HOST']+ '/' + settings.MEDIA_URL + user.fb_user_id + '/picture1_portrait.jpg'
        user.save()
        return JsonResponse(response_dict)
    else:
        return HttpResponse(status=400)


@csrf_exempt
@custom_authenticate
def user(request,user):
    if request.method == 'PATCH':
        json_data = json.loads(request.body)
        for key, value in json_data.iteritems():
            if key == 'real_auth_token':
                continue
            elif re.match('^picture', key) and re.match('_url$', key):
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


            elif re.match('^picture', key) and not re.match('_url$', key):
                continue
            setattr(user, key, value)
        user.save()
        return HttpResponse(status=200)

    elif request.method == 'GET':
        details = {
            'interested_in': user.interested_in,
            'occupation': user.occupation,
            'name': user.name,
            'age': user.age,
            'gender': user.gender,
            'education': user.education,
            'profile_picture': request.META['HTTP_HOST']+ '/' + settings.MEDIA_URL + user.fb_user_id + '/picture1_square.jpg'
        }
        return JsonResponse(details)

"""
@csrf_exempt
@custom_authenticate
def dates(request, user, day):
    if settings.DEBUG:
        response_dict = [hardcoded_dates.date1, hardcoded_dates.date2, hardcoded_dates.date3, hardcoded_dates.date4,
                         hardcoded_dates.date5, hardcoded_dates.date6, hardcoded_dates.date7]
        return JsonResponse(response_dict, safe=False)
"""

@csrf_exempt
@custom_authenticate
def date(request, user, date_id):
    if request.method == 'GET':
        day = request.GET.get('day', None)
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
            date.expires_at = nextDayOfWeekToDatetime(timezone.now(), date.day)
            date.expires_at = date.expires_at.replace(hour=23,minute=59, second=0, microsecond=0)
            #TODO: Send notification to match_user
        # If it's a like, but other user has passed notify user after two hours that they've been passed on
        elif request_json['status'] == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.PASS.value:
            # TODO: Test this in production. This code is not properly being tested
            date.expires_at = timezone.now() + datetime.timedelta(hours=24)
            transaction.on_commit(lambda: notifyUserPassedOn.apply_async(user1_id=getattr(date, request_user).pk,
                                                                         user2_id=getattr(date, match_user).pk,
                                                                         date_id=date.pk,
                                                                         countdown=60*60*2))
        # If it's a like and the other user hasn't responded, add 24 hours to the expires_at time
        elif request_json['status'] == DateStatus.LIKES.value and getattr(date, match_user+'_likes') == DateStatus.UNDECIDED.value:
            date.expires_at = timezone.now() + datetime.timedelta(hours=24)
            # TODO: Send notification to match user
        elif request_json['status'] == DateStatus.PASS.value and getattr(date, match_user+'_likes') == DateStatus.LIKES.value:
            # Notify user after two hours that they've been passed on
            # TODO: Test this in production. This code is not properly being tested
            transaction.on_commit(lambda: notifyUserPassedOn.apply_async(user1_id=getattr(date, match_user).pk,
                                                                         user2_id=getattr(date, request_user).pk,
                                                                         date_id=date.pk,
                                                                         countdown=60 * 60 * 2))
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


