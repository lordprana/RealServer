import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from api.auth import custom_authenticate
from messaging.models import Message
from api.models import User

# Create your views here.
@csrf_exempt
@custom_authenticate
@transaction.atomic
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
        return JsonResponse(json.dumps(messages_json), safe=False)

    elif request.method == 'POST':
        json_data = json.loads(request.body)
        match_user = json_data.get('match_user', None)
        message_content = json_data.get('message_content', None)
        if match_user == None or message_content == None:
            return HttpResponse(status=400)
        try:
            last_message = Message.objects.raw('SELECT * FROM messaging_message '
                                       'WHERE (sent_by_id=%s OR sent_by_id=%s) AND (sent_to_id=%s OR sent_to_id=%s)'
                                       'ORDER BY index DESC LIMIT 1',
                                       [user.fb_user_id, match_user, user.fb_user_id, match_user])[0]
            message_index = last_message.index + 1
        except IndexError:
            message_index = 0
        Message.objects.create(index=message_index, content=message_content, sent_by=user, sent_to=User.objects.get(pk=match_user))
        return HttpResponse(status=200)



    else:
        return HttpResponse(status=400)
