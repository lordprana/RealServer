# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-17 18:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20170117_1839'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='picture2_url',
            new_name='picture2_portrait_url',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='picture3_url',
            new_name='picture3_portrait_url',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='picture4_url',
            new_name='picture4_portrait_url',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='picture5_url',
            new_name='picture5_portrait_url',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='picture6_url',
            new_name='picture6_portrait_url',
        ),
    ]
