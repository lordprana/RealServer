import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from api.auth import custom_authenticate
from messaging.models import Message
from api.models import User
from api.notifications import sendMessageNotification
from matchmaking.models import Date

# Create your views here.
@csrf_exempt
@custom_authenticate
def messages(request, user):
    if request.method == 'GET':
        match_user = request.GET.get('match_user', None)
        message_index = request.GET.get('message_index', None)
        if not match_user:
            return HttpResponse(status=400)
        if not message_index:
            messages = Message.objects.raw('SELECT * FROM messaging_message '
                                                'WHERE (sent_by_id=%s OR sent_by_id=%s) AND (sent_to_id=%s OR sent_to_id=%s) '
                                                'ORDER BY index DESC LIMIT 20 ',
                                           [user.fb_user_id,match_user,user.fb_user_id,match_user])
        else:
            messages = Message.objects.raw('SELECT * FROM messaging_message '
                                                'WHERE (sent_by_id=%s OR sent_by_id=%s) AND (sent_to_id=%s OR sent_to_id=%s) '
                                                'AND index<%s '
                                                'ORDER BY index DESC LIMIT 20',
                                           [user.fb_user_id,match_user,user.fb_user_id,match_user,message_index])
        messages_json = []
        for message in messages:
            json_entry = \
                {
                    'message_id': message.id,
                    'message_index': message.index,
                    'message_content': message.content,
                    'time_sent': message.time_sent.isoformat(),
                    'sent_by_match': True if message.sent_by.pk==match_user else False
                }
            messages_json.append(json_entry)
            if message.sent_by.pk==match_user:
                message.read = True
            message.save()
        return JsonResponse(messages_json, safe=False)

    elif request.method == 'POST':
        with transaction.atomic():
            json_data = json.loads(request.body)
            match_user = json_data.get('match_user', None)
            message_content = json_data.get('message_content', None)
            match_user = User.objects.select_for_update(nowait=True).get(pk=match_user)
            user = User.objects.select_for_update(nowait=True).get(pk=user.pk)
            date_id = json_data.get('date_id', None)
            date = Date.objects.get(pk=date_id)
            if match_user == None or message_content == None or date_id == None:
                return HttpResponse(status=400)
            try:
                last_message = Message.objects.raw('SELECT * FROM messaging_message '
                                           'WHERE (sent_by_id=%s OR sent_by_id=%s) AND (sent_to_id=%s OR sent_to_id=%s)'
                                           'ORDER BY index DESC LIMIT 1',
                                           [user.pk, match_user.pk, user.pk, match_user.pk])[0]
                message_index = last_message.index + 1
            except IndexError:
                message_index = 0
            Message.objects.create(index=message_index, content=message_content, sent_by=user,
                                   sent_to=match_user, date=date)
            sendMessageNotification(user, match_user, date)
        return HttpResponse(status=200)



    else:
        return HttpResponse(status=400)
