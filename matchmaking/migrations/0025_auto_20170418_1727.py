# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-18 17:27
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0024_auto_20170417_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='yelpbusinessdetails',
            name='place_url',
            field=models.CharField(default='not_set', max_length=300),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 4, 18, 17, 27, 12, 23004, tzinfo=utc)),
        ),
    ]
