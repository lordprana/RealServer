# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-07 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20170131_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fcmdevice',
            name='registration_token',
            field=models.CharField(max_length=300),
        ),
    ]