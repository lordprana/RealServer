# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-18 17:57
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0025_auto_20170418_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 4, 18, 17, 56, 44, 787214, tzinfo=utc)),
        ),
    ]
