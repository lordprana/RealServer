# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-20 23:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0018_auto_20170320_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 3, 20, 23, 46, 1, 495783, tzinfo=utc)),
        ),
    ]