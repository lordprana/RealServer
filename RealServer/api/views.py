from django.shortcuts import render
from rest_framework.authtoken.models import Token
from api.auth import custom_authenticate
from api import hardcoded_dates
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
# Create your views here.


@csrf_exempt
@custom_authenticate
def user(request, user):
    if request.method == 'POST':
        token = Token.objects.get(user=user)
        response_dict = {
            'fb_user_id' : user.fb_user_id,
            'real_auth_token': token.key
        }
        return JsonResponse(response_dict)

@csrf_exempt
@custom_authenticate
def dateslist(request, user):
    if settings.DEBUG:
        response_dict = [hardcoded_dates.date1, hardcoded_dates.date2, hardcoded_dates.date3, hardcoded_dates.date4,
                         hardcoded_dates.date5, hardcoded_dates.date6, hardcoded_dates.date7]
        return JsonResponse(response_dict, safe=False)