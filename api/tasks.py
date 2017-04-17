# Create your tasks here
from __future__ import absolute_import, unicode_literals

#from celery import shared_task
from RealServer.celery import app

from celery.task import periodic_task
from celery.task.schedules import crontab

from api.models import User
from api.notifications import sendPassNotification, sendUpcomingDateNotification
from matchmaking.models import Date, YelpBusinessHours
from matchmaking.yelp import refreshPlaceHoursOnNetwork

import sys
from datetime import timedelta


@periodic_task(run_every=timedelta(seconds=10))
def print_test():
    print('test')

@periodic_task(run_every=crontab(minute=0, hour=8))
def refreshPlaceHours():
    print('Refreshing place hours from Yelp')
    businesses = YelpBusinessHours.objects.all()
    for b in businesses:
        place_hours = refreshPlaceHoursOnNetwork(b.place_id)
        place_hours.save()


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