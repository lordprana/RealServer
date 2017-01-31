# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-26 18:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0003_mutualfriend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mutualfriend',
            name='date',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matchmaking.Date'),
        ),
    ]