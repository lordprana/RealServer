# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-09 15:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0008_auto_20170209_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mutualfriend',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 2, 9, 15, 37, 8, 218670, tzinfo=utc)),
        ),
    ]
