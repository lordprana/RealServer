# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-15 15:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0026_auto_20170418_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 5, 15, 15, 40, 46, 655135, tzinfo=utc)),
        ),
    ]
