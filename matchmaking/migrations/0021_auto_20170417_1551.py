# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-17 15:51
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0020_auto_20170406_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='YelpBusinessHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_id', models.CharField(max_length=300)),
                ('mon_start_time', models.TimeField()),
                ('mon_end_time', models.TimeField()),
                ('tue_start_time', models.TimeField()),
                ('tue_end_time', models.TimeField()),
                ('wed_start_time', models.TimeField()),
                ('wed_end_time', models.TimeField()),
                ('thur_start_time', models.TimeField()),
                ('thur_end_time', models.TimeField()),
                ('fri_start_time', models.TimeField()),
                ('fri_end_time', models.TimeField()),
                ('sat_start_time', models.TimeField()),
                ('sat_end_time', models.TimeField()),
                ('sun_start_time', models.TimeField()),
                ('sun_end_time', models.TimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='date',
            name='date_of_date',
            field=models.DateField(default=datetime.datetime(2017, 4, 17, 15, 51, 55, 403352, tzinfo=utc)),
        ),
    ]
