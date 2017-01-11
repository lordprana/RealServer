from __future__ import unicode_literals

from django.db import models
from api.models import User
from matchmaking.models import Date
# Create your models here.

class Message(models.Model):
    index = models.IntegerField()
    content = models.CharField(max_length=480)
    time_sent = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey('api.User', related_name='sent_by')
    sent_to = models.ForeignKey('api.User', related_name='sent_to')
    read = models.BooleanField(default=False)
    date = models.ForeignKey(Date,)
#TODO:Blocking Add Foreign Key to Date associated with this message




