from api.models import FCMDevice
from matchmaking.models import DateCategories
import requests
import json
from RealServer.settings import FCM_SERVER_API_KEY

def sendMatchNotification(request_user, match_user):
    devices = FCMDevice.objects.filter(user=match_user)
    for device in devices:
        request_body = {
            'notification': {
                'body': request_user.first_name + ' made it Real!',
                'sound': 'default'
            },
            'to': device.registration_token,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + FCM_SERVER_API_KEY
        }
        response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(request_body), headers=headers)
        json_response = json.loads(response.content)
        handleNotificationResponse(json_response, device)
        # If Unavailable, try to resend one more time
        if json_response['results'][0].get('error', None) == 'Unavailable':
            response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(request_body), headers=headers)
            json_response = json.loads(response.content)
            handleNotificationResponse(json_response, device)

def sendLikeNotification(request_user, like_user, date):
    android_devices = FCMDevice.objects.filter(user=like_user)
    # Change body depending on date category
    if date.category == DateCategories.FOOD.value:
        request_text = request_user.first_name + ' wants to grab a bite with you!'
    elif date.category == DateCategories.COFFEE.value:
        request_text = request_user.first_name + ' wants to grab a coffee with you!'
    elif date.category == DateCategories.DRINKS.value:
        request_text = request_user.first_name + ' wants to grab a drink with you!'
    elif date.category == DateCategories.PARKS.value:
        request_text = request_user.first_name + ' wants to explore a park with you!'
    elif date.category == DateCategories.MUSEUMS.value:
        request_text = request_user.first_name + ' wants to check out a museum with you!'
    elif date.category == DateCategories.FUN.value:
        request_text = request_user.first_name + ' wants to try something fun with you!'

    for device in android_devices:
        request_body = {
            'notification': {
                'body': request_text,
                'sound': 'default'
            },
            'to': device.registration_token,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + FCM_SERVER_API_KEY
        }
        response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(request_body), headers=headers)
        json_response = json.loads(response.content)
        handleNotificationResponse(json_response, device)
        # If Unavailable, try to resend one more time
        if json_response['results'][0].get('error', None) == 'Unavailable':
            response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(request_body), headers=headers)
            json_response = json.loads(response.content)
            handleNotificationResponse(json_response, device)

def sendPassNotification(passer_user, passed_user):
    android_devices = FCMDevice.objects.filter(user=passed_user)
    for device in android_devices:
        request_body = {
            'notification': {
                'body': passer_user.first_name + ' has passed on your date. Bummer.',
                'sound': 'default'
            },
            'to': device.registration_token,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + FCM_SERVER_API_KEY
        }
        response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(request_body), headers=headers)
        json_response = json.loads(response.content)
        handleNotificationResponse(json_response, device)
        # If Unavailable, try to resend one more time
        if json_response['results'][0].get('error', None) == 'Unavailable':
            response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(request_body), headers=headers)
            json_response = json.loads(response.content)
            handleNotificationResponse(json_response, device)

def handleNotificationResponse(json_response, device):
    if json_response['results'][0].get('error', None) == 'Unavailable':
        return False
    elif json_response['results'][0].get('error', None) == 'NotRegistered' or \
                    json_response['results'][0].get('error', None) == 'InvalidRegistration':
        device.delete()
        return False
    elif json_response['results'][0].get('registration_id', None):
        device.registration_token = json_response['results'][0].get('registration_id', None)
        device.save()
        return True
    else:
        return True
