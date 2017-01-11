from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from matchmaking.models import Date

from enum import Enum

class SexualPreference(Enum):
    WOMEN = 'w'
    MEN = 'm'
    BISEXUAL = 'b'

class Gender(Enum):
    WOMAN = 'w'
    MAN = 'm'

# Create your models here.
class User(AbstractBaseUser):
    USERNAME_FIELD = 'fb_user_id'

    fb_user_id = models.CharField(max_length=300, primary_key=True)
    most_recent_fb_auth_token = models.CharField(max_length=300)

    name = models.CharField(max_length=200, null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=1, null=True)
    interested_in = models.CharField(max_length=1, null=True)
    occupation = models.CharField(max_length=50, null=True)
    education = models.CharField(max_length=50, null=True)
    about = models.CharField(max_length=500, null=True)

    min_age_preference = models.IntegerField(default=18)
    max_age_preference = models.IntegerField(default=35)

    max_price = models.IntegerField(default=2)

    search_radius = models.IntegerField(default=24) #25 is max radius for Yelp API
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

    sunday_start_time = models.TimeField(blank=True, null=True)
    sunday_end_time = models.TimeField(blank=True, null=True)
    monday_start_time = models.TimeField(blank=True, null=True)
    monday_end_time = models.TimeField(blank=True, null=True)
    tuesday_start_time = models.TimeField(blank=True, null=True)
    tuesday_end_time = models.TimeField(blank=True, null=True)
    wednesday_start_time = models.TimeField(blank=True, null=True)
    wednesday_end_time = models.TimeField(blank=True, null=True)
    thursday_start_time = models.TimeField(blank=True, null=True)
    thursday_end_time = models.TimeField(blank=True, null=True)
    friday_start_time = models.TimeField(blank=True, null=True)
    friday_end_time = models.TimeField(blank=True, null=True)
    saturday_start_time = models.TimeField(blank=True, null=True)
    saturday_end_time = models.TimeField(blank=True, null=True)

    sun_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    mon_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    tue_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    wed_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    thur_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    fri_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)
    sat_date = models.ForeignKey('matchmaking.Date', related_name="+", null=True, unique=False)

    picture1 = models.URLField(null=True)
    picture2 = models.URLField(null=True)
    picture3 = models.URLField(null=True)
    picture4 = models.URLField(null=True)
    picture5 = models.URLField(null=True)
    picture6 = models.URLField(null=True)


    def __unicode__(self):
        if self.first_name and self.last_name:
            return self.first_name + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return "No name provided"