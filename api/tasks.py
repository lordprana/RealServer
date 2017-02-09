# Create your tasks here
from __future__ import absolute_import, unicode_literals

#from celery import shared_task
from RealServer.celery import app

from api.models import User
from api.notifications import sendPassNotification
from matchmaking.models import Date
import sys



@app.task
def notifyUserPassedOn(user1_id, user2_id, date_id):
    user1 = User.objects.get(pk=user1_id)
    user2 = User.objects.get(pk=user2_id)
    date = Date.objects.get(pk=date_id)
    date.expires_at = date.original_expires_at
    date.save()
    user1.passed_matches.add(user2)
    sendPassNotification(user1, user2)