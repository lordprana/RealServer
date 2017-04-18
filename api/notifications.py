from api.models import FCMDevice
from matchmaking.models import DateCategories
import requests
import json
from RealServer.settings import FCM_SERVER_API_KEY
from api.models import OperatingSystem, Status

def sendNotification(message, type, date_id, device):
    print("This is a test of the notification system")
    print(device.operating_system)
    if device.operating_system == OperatingSystem.ANDROID.value:
        request_body = {
            'data': {
                'message': message,
                'type': type,
                'date_id': date_id
            },
            'to': device.registration_token,
        }
    elif device.operating_system == OperatingSystem.iOS.value:
        request_body = {
            'notification': {
                'body': message
            },
            'data': {
                'message': message,
                'type': type,
                'date_id': date_id
            },
            'to': device.registration_token,
        }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + FCM_SERVER_API_KEY
    }
    print(request_body)
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

def sendMatchNotification(request_user, match_user, date):
    # Don't send message if user has specified notification preference in settings
    if not match_user.new_matches_notification:
        return
    # Don't send messages if user has logged out of the app
    if match_user.status == Status.INACTIVE.value:
        return

    devices = FCMDevice.objects.filter(user=match_user)
    for device in devices:
        message = request_user.first_name + ' made it Real!'
        type = 'match'
        sendNotification(message, type, date.pk, device)

def sendLikeNotification(request_user, like_user, date):
    # Don't send message if user has specified notification preference in settings
    if not like_user.new_likes_notification:
        return
    # Don't send messages if user has logged out of the app
    if like_user.status == Status.INACTIVE.value:
        return

    devices = FCMDevice.objects.filter(user=like_user)
    # Change body depending on date category
    if date.category == DateCategories.FOOD.value:
        message = request_user.first_name + ' wants to grab a bite with you!'
    elif date.category == DateCategories.COFFEE.value:
        message = request_user.first_name + ' wants to grab a coffee with you!'
    elif date.category == DateCategories.DRINKS.value:
        message = request_user.first_name + ' wants to grab a drink with you!'
    elif date.category == DateCategories.PARKS.value:
        message = request_user.first_name + ' wants to explore a park with you!'
    elif date.category == DateCategories.MUSEUMS.value:
        message = request_user.first_name + ' wants to check out a museum with you!'
    elif date.category == DateCategories.FUN.value:
        message = request_user.first_name + ' wants to try something fun with you!'

    for device in devices:
        type = 'like'
        sendNotification(message, type, date.pk, device)

def sendPassNotification(passer_user, passed_user, date):
    # Don't send message if user has specified notification preference in settings
    if not passed_user.pass_notification:
        return
    # Don't send messages if user has logged out of the app
    if passed_user.status == Status.INACTIVE.value:
        return

    devices = FCMDevice.objects.filter(user=passed_user)
    for device in devices:
        message = passer_user.first_name + ' has passed on your date.'
        type = 'pass'
        sendNotification(message, type, date.pk, device)

def sendMessageNotification(messenger_user, receiver_user, date):
    # Don't send message if user has specified notification preference in settings
    if not receiver_user.new_messages_notification:
        return
    # Don't send messages if user has logged out of the app
    if receiver_user.status == Status.INACTIVE.value:
        return

    devices = FCMDevice.objects.filter(user=receiver_user)
    for device in devices:
        message = messenger_user.first_name + ' sent you a message.'
        type = 'message'
        sendNotification(message, type, date.pk, device)

def sendUpcomingDateNotification(messenger_user, receiver_user, date):
    # Don't send message if user has specified notification preference in settings
    if not receiver_user.new_messages_notification:
        return
    # Don't send messages if user has logged out of the app
    if receiver_user.status == Status.INACTIVE.value:
        return

    devices = FCMDevice.objects.filter(user=receiver_user)
    for device in devices:
        message = 'You have a date with ' + messenger_user.first_name + ' tomorrow!'
        type = 'reminder'
        sendNotification(message, type, date.pk, device)


