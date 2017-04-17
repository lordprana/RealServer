from __future__ import unicode_literals

from django.db import models
from enum import Enum
from datetime import date, time
from django.utils import timezone

class DateStatus(Enum):
    LIKES = 'l'
    PASS = 'p'
    UNDECIDED = 'u'

class DateCategories(Enum):
    DRINKS = 'drinks'
    FOOD = 'food'
    COFFEE = 'coffee'
    PARKS = 'parks'
    MUSEUMS = 'museums'
    FUN = 'fun'

# Create your models here.
class Date(models.Model):
    user1 = models.ForeignKey('api.User', related_name="+")
    user2 = models.ForeignKey('api.User', related_name="+")

    original_expires_at = models.DateTimeField() # The expires_at field set when this Date is first created.
    expires_at = models.DateTimeField()
    day = models.CharField(max_length=4)
    date_of_date = models.DateField(default=timezone.now()) # Added this default value to fix bug
    start_time = models.TimeField()
    user1_likes = models.CharField(max_length=1, default=DateStatus.UNDECIDED.value)
    user2_likes = models.CharField(max_length=1, default=DateStatus.UNDECIDED.value)
    place_id = models.CharField(max_length=300)
    place_name = models.CharField(max_length=300)
    category = models.CharField(max_length=20)
    inspected_match = models.BooleanField(default=False)
    passed_user_notified = models.BooleanField(default=False)

    appropriate_times = {
        'drinks':
        {
            'start': time(hour=15),
            'end': time(hour=23, minute=59, second=59)
        },
        'food':
        {
            'start': time(hour=12),
            'end': time(hour=23)
        },
        'coffee':
        {
            'start': time(hour=7),
            'end': time(hour=20, minute=30)
        },
        'parks':
        {
            'start': time(hour=7),
            'end': time(hour=18)
        },
        'museums':
        {
            'start': time(hour=10),
            'end': time(hour=22)
        },
        'fun':
        {
            'start': time(hour=7),
            'end': time(hour=22)
        }
    }

class MutualFriend(models.Model):
    first_name = models.CharField(max_length=200)
    picture = models.URLField()
    date = models.ForeignKey(Date)

class YelpBusinessHours(models.Model):
    place_id = models.CharField(max_length=300)
    mon_start_time = models.TimeField(null=True)
    mon_end_time = models.TimeField(null=True)
    tue_start_time = models.TimeField(null=True)
    tue_end_time = models.TimeField(null=True)
    wed_start_time = models.TimeField(null=True)
    wed_end_time = models.TimeField(null=True)
    thur_start_time = models.TimeField(null=True)
    thur_end_time = models.TimeField(null=True)
    fri_start_time = models.TimeField(null=True)
    fri_end_time = models.TimeField(null=True)
    sat_start_time = models.TimeField(null=True)
    sat_end_time = models.TimeField(null=True)
    sun_start_time = models.TimeField(null=True)
    sun_end_time = models.TimeField(null=True)

class YelpAccessToken(models.Model):
    access_token = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

