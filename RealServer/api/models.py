from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
class User(AbstractBaseUser):
    USERNAME_FIELD = 'fb_user_id'

    fb_user_id = models.CharField(max_length=300, primary_key=True)
    most_recent_fb_auth_token = models.CharField(max_length=300)

    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    age = models.IntegerField(null=True)
    interested_in = models.CharField(max_length=1, null=True)
    occupation = models.CharField(max_length=50, null=True)
    education = models.CharField(max_length=50, null=True)
    about_me = models.CharField(max_length=500, null=True)

    # Add pictures once we know the correct dimensions

    likes_drinks = models.NullBooleanField(default=False, null=True)
    likes_food = models.NullBooleanField(default=False, null=True)
    likes_coffee = models.NullBooleanField(default=False, null=True)
    likes_nature = models.NullBooleanField(default=False, null=True)
    likes_culture = models.NullBooleanField(default=False, null=True)
    likes_active = models.NullBooleanField(default=False, null=True)

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
    sunday_start_time = models.TimeField(blank=True, null=True)
    sunday_end_time = models.TimeField(blank=True, null=True)

class RealAuthTokens(models.Model):
    token = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE)