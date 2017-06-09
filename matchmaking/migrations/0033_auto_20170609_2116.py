# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-09 21:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0032_auto_20170603_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcludedBusiness',
            fields=[
                ('place_id', models.CharField(max_length=300, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 9, 21, 16, 47, 96461, tzinfo=utc)),
        ),
    ]
