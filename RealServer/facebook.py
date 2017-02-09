import hashlib
import hmac
import json
import urllib

import requests

from RealServer.settings import FB_APP_ID, FB_APP_SECRET

"""
Takes a fb_auth_token and returns a fb_user_id
"""
def getUserId(fb_auth_token):
    request_url = 'https://graph.facebook.com/debug_token?input_token=' + fb_auth_token + \
                  '&access_token=' + FB_APP_ID + '|' + FB_APP_SECRET
    response = requests.get(request_url)
    return response.json()['data']['user_id']

def getAppSecretProof(app_secret, access_token):
    h = hmac.new (
        app_secret.encode('utf-8'),
        msg=access_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return h.hexdigest()

def getMutualFriends(user, match):
    app_secret_proof = getAppSecretProof(FB_APP_SECRET, user.most_recent_fb_auth_token)
    request_url = 'https://graph.facebook.com/v2.8/' + match.fb_user_id +\
                  '?fields=context.fields(all_mutual_friends.limit(10))&'+\
                  'access_token=' + user.most_recent_fb_auth_token +\
                  '&appsecret_proof=' + app_secret_proof
    try:
        return requests.get(request_url).json()['context']['all_mutual_friends']
    except KeyError:
        return None

def getUserInfo(user):
    app_secret_proof = getAppSecretProof(FB_APP_SECRET, user.most_recent_fb_auth_token)
    request_url = 'https://graph.facebook.com/v2.8/' + user.fb_user_id + \
                  '?access_token=' + user.most_recent_fb_auth_token + \
                  '&appsecret_proof=' + app_secret_proof + \
                  '&fields=birthday,education,gender,interested_in,first_name,last_name,work'
    return requests.get(request_url).json()

def getUserProfilePicture(user):
    app_secret_proof = getAppSecretProof(FB_APP_SECRET, user.most_recent_fb_auth_token)
    # Picture.height > 960 for highest resolution
    request_url = 'https://graph.facebook.com/v2.8/' + user.fb_user_id + '?fields=picture.height(961)' + \
                  '&access_token=' + user.most_recent_fb_auth_token + \
                  '&appsecret_proof=' + app_secret_proof
    response = requests.get(request_url)
    response_json = json.loads(response.content)
    if response.status_code == 200 and response_json['picture']['data']['url']:
        #picture = urllib.urlopen(response_json['picture']['data']['url'])
        picture = requests.get(response_json['picture']['data']['url'])
        return picture.content
    else:
        return None