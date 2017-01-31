from api.models import FCMDevice
import requests
import json
from RealServer.settings import FCM_SERVER_API_KEY

def sendMatchNotification(request_user, match_user):
    android_devices = FCMDevice.objects.filter(user=match_user)
    for device in android_devices:
        request_body = {
            'notification': {
                "body": request_user.name + " made it Real!"
            },
            'to': device.registration_token
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + FCM_SERVER_API_KEY
        }
        response = requests.post('https://fcm.googleapis.com/fcm/send', data=request_body, headers=headers)
        json_response = json.loads(response.content)
        # If Unavailable, try to resend one more time
        if json_response['results'][0].get('error', None) == 'Unavailable':
            response = requests.post('https://fcm.googleapis.com/fcm/send', data=request_body, headers=headers)
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
