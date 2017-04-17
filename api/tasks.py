# Create your tasks here
from __future__ import absolute_import, unicode_literals

#from celery import shared_task
from RealServer.celery import app

from api.models import User
from api.notifications import sendPassNotification, sendUpcomingDateNotification
from matchmaking.models import Date
import sys

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, test.s('hello'))

@app.task
def test(arg):
    print(arg)

@app.task
def notifyUserPassedOn(user1_id, user2_id, date_id):
    user1 = User.objects.get(pk=user1_id)
    user2 = User.objects.get(pk=user2_id)
    date = Date.objects.get(pk=date_id)
    date.passed_user_notified = True
    date.expires_at = date.original_expires_at
    date.save()
    user1.passed_matches.add(user2)
    sendPassNotification(user1, user2, date)

@app.task
def notifyUpcomingDate(user1_id, user2_id, date_id):
    user1 = User.objects.get(pk=user1_id)
    user2 = User.objects.get(pk=user2_id)
    date = Date.objects.get(pk=date_id)
    sendUpcomingDateNotification(user1, user2, date)
    sendUpcomingDateNotification(user2, user1, date)