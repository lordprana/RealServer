# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-06 14:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_user_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='fri_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='matchmaking.Date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='mon_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='matchmaking.Date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='sat_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='matchmaking.Date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='sun_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='matchmaking.Date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='thur_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='matchmaking.Date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tue_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='matchmaking.Date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='wed_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='matchmaking.Date'),
        ),
    ]