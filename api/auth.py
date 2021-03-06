import json

from django.contrib.auth import authenticate
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from RealServer import settings

from RealServer import facebook
from api.models import User


def custom_authenticate(view):
    def view_wrapper(request, user=None, user_id=None, *args, **kwargs):
        if (request.method == 'POST' or request.method == 'PATCH' or request.method == 'PUT'):
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
        # Fake users don't have to authenticate
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
            try:
                token = Token.objects.get(user=user)
                if (token.key == real_auth_token):
                    if fb_auth_token:
                        user.most_recent_fb_auth_token = fb_auth_token
                        user.save()
                    return user
            except Token.DoesNotExist: # Token does not exist in case of fake_user
                if user.is_fake_user:
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