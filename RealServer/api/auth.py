import requests
from RealServer.settings import FB_APP_SECRET, FB_APP_ID
from api.models import User
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from django.contrib.auth import authenticate
from RealServer import facebook
import json

def custom_authenticate(view):
    def view_wrapper(request, user=None, user_id=None, *args, **kwargs):
        if (request.method == 'POST' or request.method == 'PATCH'):
            json_data = json.loads(request.body)
            fb_user_id = json_data.get('fb_user_id', None)
            fb_auth_token = json_data.get('fb_auth_token', None)
            real_auth_token = json_data.get('real_auth_token', None)
        elif (request.method == 'GET'):
            fb_user_id = request.GET.get('fb_user_id', None)
            fb_auth_token = request.GET.get('fb_auth_token', None)
            real_auth_token = request.GET.get('real_auth_token', None)
        if user_id:
            fb_user_id = user_id
        if fb_auth_token and fb_user_id and real_auth_token:
            user=authenticate(fb_user_id=fb_user_id, fb_auth_token=fb_auth_token, real_auth_token=real_auth_token)
        elif fb_auth_token and fb_user_id:
            user = authenticate(fb_user_id=fb_user_id, fb_auth_token=fb_auth_token)
        elif real_auth_token and fb_user_id:
            user = authenticate(fb_user_id=fb_user_id, real_auth_token=real_auth_token)
        else:
            return HttpResponse(status=400)
        if user:
            return view(request, user, *args, **kwargs)
        else:
            return HttpResponse(status=403)
    return view_wrapper

class AuthenticationBackend(object):
    def authenticate(self, fb_user_id, fb_auth_token=None, real_auth_token=None):
        if real_auth_token:
            try:
                user = User.objects.get(fb_user_id=fb_user_id)
            except User.DoesNotExist:
                return None
            token = Token.objects.get(user=user)
            if (token.key == real_auth_token):
                if fb_auth_token:
                    user.most_recent_fb_auth_token = fb_auth_token
                    user.save()
                return user
        elif fb_auth_token:
            try:
                response_user_id = facebook.getUserId(fb_auth_token)
            except KeyError:
                return None
            if fb_user_id == response_user_id:
                try:
                    user = User.objects.get(fb_user_id=fb_user_id)
                    user.most_recent_fb_auth_token = fb_auth_token
                    user.save()
                    return user
                except User.DoesNotExist:
                    user = User(fb_user_id=fb_user_id, most_recent_fb_auth_token=fb_auth_token)
                    user.save()
                    real_auth_token = Token.objects.create(user=user)
                    return user
            else:
                return None
        return None

    def get_user(self,fb_user_id):
        try:
            return User.objects.get(fb_user_id=fb_user_id)
        except User.DoesNotExist:
            return None