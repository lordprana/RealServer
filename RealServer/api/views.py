from django.shortcuts import render
from rest_framework.authtoken.models import Token
from api.auth import custom_authenticate
from api import hardcoded_dates
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
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
        return JsonResponse(response_dict)

@csrf_exempt
@custom_authenticate
def user(request,user):
    if request.method == 'PATCH':
        return HttpResponse(status=200)

@csrf_exempt
@custom_authenticate
def dates(request, user):
    if settings.DEBUG:
        response_dict = [hardcoded_dates.date1, hardcoded_dates.date2, hardcoded_dates.date3, hardcoded_dates.date4,
                         hardcoded_dates.date5, hardcoded_dates.date6, hardcoded_dates.date7]
        return JsonResponse(response_dict, safe=False)

@csrf_exempt
@custom_authenticate
def date(request, user, date_id):
    if request.method == 'PATCH':
        request_json = json.loads(request.body)
        return HttpResponse(status=200)

@csrf_exempt
@custom_authenticate
def report_and_block(request, user):
    if request.method == 'POST':
        request_json = json.loads(request.body)
        print request_json.get('blocked_user_id', None)
        print request_json.get('report_text' , None)
        return HttpResponse(status=200)
