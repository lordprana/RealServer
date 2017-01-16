from django.shortcuts import render
from rest_framework.authtoken.models import Token
from api.auth import custom_authenticate
from api import hardcoded_dates
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import re
import os
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
        user.education = user_json['education']
        user.gender = user_json['gender']
        user.interested_in = user_json['interested_in']
        user.name = user_json['name']
        user.work = user_json['work']

        user_picture = facebook.getUserProfilePicture(user)
        if not os.path.exists(settings.MEDIA_ROOT + user.fb_user_id):
            os.makedirs(settings.MEDIA_ROOT + user.fb_user_id)
        f = open(settings.MEDIA_ROOT + user.fb_user_id + '/' + 'picture_1.jpg', 'w')
        f.write(user_picture.content)



        return JsonResponse(response_dict)
    else:
        return HttpResponse(status=400)

#TODO: Blocking
@csrf_exempt
@custom_authenticate
def user(request,user):
    if request.method == 'PATCH':
        json_data = json.loads(request.body)
        for key, value in json_data.iteritems():
            if key == 'real_auth_token':
                continue
            elif re.match('^picture') and re.match('_url$'):
                if re.match('^picture') and not re.match('_url$'):
                    #TODO: Add image processing
                    continue
            setattr(user, key, value)
        user.save()
        return HttpResponse(status=200)

#TODO: Blocking
@csrf_exempt
@custom_authenticate
def dates(request, user):
    if settings.DEBUG:
        response_dict = [hardcoded_dates.date1, hardcoded_dates.date2, hardcoded_dates.date3, hardcoded_dates.date4,
                         hardcoded_dates.date5, hardcoded_dates.date6, hardcoded_dates.date7]
        return JsonResponse(response_dict, safe=False)

#TODO: Blocking
@csrf_exempt
@custom_authenticate
def date(request, user, date_id):
    if request.method == 'PATCH':
        request_json = json.loads(request.body)
        return HttpResponse(status=200)

#TODO: Blocking
@csrf_exempt
@custom_authenticate
def report_and_block(request, user):
    if request.method == 'POST':
        request_json = json.loads(request.body)
        print request_json.get('blocked_user_id', None)
        print request_json.get('report_text' , None)
        return HttpResponse(status=200)
