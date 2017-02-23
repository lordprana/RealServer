# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-23 18:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0012_auto_20170221_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='date',
            name='passed_user_notified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 2, 23, 18, 50, 19, 459500, tzinfo=utc)),
        ),
    ]
