from __future__ import unicode_literals

from django.db import models
from enum import Enum
from datetime import date

class DateStatus(Enum):
    LIKES = 'l'
    PASS = 'p'
    UNDECIDED = 'u'

class DateCategories(Enum):
    DRINKS = 'drinks'
    FOOD = 'food'
    COFFEE = 'coffee'
    NATURE = 'nature'
    CULTURE = 'culture'
    ACTIVE = 'active'

# Create your models here.
class Date(models.Model):
    user1 = models.ForeignKey('api.User', related_name="+")
    user2 = models.ForeignKey('api.User', related_name="+")
    expires_at = models.DateTimeField()
    day = models.CharField(max_length=4)
    start_time = models.TimeField()
    user1_likes = models.CharField(max_length=1, default=DateStatus.UNDECIDED.value)
    user2_likes = models.CharField(max_length=1, default=DateStatus.UNDECIDED.value)
    place_id = models.CharField(max_length=300)
    category = models.CharField(max_length=20)

class YelpAccessToken(models.Model):
    access_token = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()