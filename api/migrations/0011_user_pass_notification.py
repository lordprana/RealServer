# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-16 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_user_is_fake_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pass_notification',
            field=models.BooleanField(default=True),
        ),
    ]
