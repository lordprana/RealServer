# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-09 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20170301_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_fake_user',
            field=models.BooleanField(default=False),
        ),
    ]
