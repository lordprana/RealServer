# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from RealServer.celery import app
from api.models import User
from matchmaking.models import Date


@app.task
def add(x, y):
    print (x + y)
    return x + y

@shared_task
def mul(x, y):
    return x * y

@shared_task
def xsum(numbers):
    return sum(numbers)

#TODO: Test this in production
#TODO: Add notification
@shared_task()
def notifyUserPassedOn(user1_id, user2_id, date_id):
    user1 = User.objects.get(pk=user1_id)
    print("Sending rejection to: " + user1.fb_user_id)
    date = Date.objects.get(pk=date_id)
    date.expires_at = date.original_expires_at
    date.save()