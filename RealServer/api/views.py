from django.shortcuts import render
from rest_framework.authtoken.models import Token
from api.auth import custom_authenticate
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
