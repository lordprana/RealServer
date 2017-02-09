from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from matchmaking.models import Date

from enum import Enum

class SexualPreference(Enum):
    WOMEN = 'w'
    MEN = 'm'
    BISEXUAL = 'b'

class Gender(Enum):
    WOMAN = 'w'
    MAN = 'm'

class Status(Enum):
    NEW_USER = 'new'
    FINISHED_PROFILE = 'finished_profile'
    INACTIVE = 'inactive'

# Create your models here.
class User(AbstractBaseUser):
    USERNAME_FIELD = 'fb_user_id'

    fb_user_id = models.CharField(max_length=300, primary_key=True)
    most_recent_fb_auth_token = models.CharField(max_length=300)

    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=1, null=True)
    interested_in = models.CharField(max_length=1, null=True)
    occupation = models.CharField(max_length=200, null=True)
    education = models.CharField(max_length=200, null=True)
    about = models.CharField(max_length=500, null=True)

    status = models.CharField(max_length=20)

    min_age_preference = models.IntegerField(default=18)
    max_age_preference = models.IntegerField(default=35)

    max_price = models.IntegerField(default=2)

    search_radius = models.IntegerField(default=24) #24 is max radius for Yelp API
    latitude = models.DecimalField(null=True, decimal_places=6, max_digits=13) # Precision within .1 meter resolution
    longitude = models.DecimalField(null=True, decimal_places=6, max_digits=13)

    passed_matches = models.ManyToManyField('self', related_name='passed_matches')

    # Add pictures once we know the correct dimensions

    likes_drinks = models.NullBooleanField(default=False, null=True)
    likes_food = models.NullBooleanField(default=False, null=True)
    likes_coffee = models.NullBooleanField(default=False, null=True)
    likes_nature = models.NullBooleanField(default=False, null=True)
    likes_culture = models.NullBooleanField(default=False, null=True)
    likes_active = models.NullBooleanField(default=False, null=True)

    sun_start_time = models.TimeField(blank=True, null=True)
    sun_end_time = models.TimeField(blank=True, null=True)
    mon_start_time = models.TimeField(blank=True, null=True)
    mon_end_time = models.TimeField(blank=True, null=True)
    tue_start_time = models.TimeField(blank=True, null=True)
    tue_end_time = models.TimeField(blank=True, null=True)
    wed_start_time = models.TimeField(blank=True, null=True)
    wed_end_time = models.TimeField(blank=True, null=True)
    thur_start_time = models.TimeField(blank=True, null=True)
    thur_end_time = models.TimeField(blank=True, null=True)
    fri_start_time = models.TimeField(blank=True, null=True)
    fri_end_time = models.TimeField(blank=True, null=True)
    sat_start_time = models.TimeField(blank=True, null=True)
    sat_end_time = models.TimeField(blank=True, null=True)

    sun_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    mon_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    tue_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    wed_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    thur_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    fri_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    sat_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)

    picture1_portrait_url = models.URLField(null=True)
    picture1_square_url = models.URLField(null=True)
    picture2_portrait_url = models.URLField(null=True)
    picture2_square_url = models.URLField(null=True)
    picture3_portrait_url = models.URLField(null=True)
    picture3_square_url = models.URLField(null=True)
    picture4_portrait_url = models.URLField(null=True)
    picture4_square_url = models.URLField(null=True)
    picture5_portrait_url = models.URLField(null=True)
    picture5_square_url = models.URLField(null=True)
    picture6_portrait_url = models.URLField(null=True)
    picture6_square_url = models.URLField(null=True)

    new_likes_notification = models.BooleanField(default=True)
    new_matches_notification = models.BooleanField(default=True)
    new_messages_notification = models.BooleanField(default=True)
    upcoming_dates_notification = models.BooleanField(default=True)

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "No name provided"

class BlockedReports(models.Model):
    blocking_user = models.ForeignKey(User, related_name='blocking_user')
    blocked_user = models.ForeignKey(User, related_name='blocked_user')
    associated_date = models.ForeignKey(Date, related_name='associated_date')
    report_content = models.CharField(max_length=10000)

class FCMDevice(models.Model):
    registration_token = models.CharField(max_length=300)
    user = models.ForeignKey(User)