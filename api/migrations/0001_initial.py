# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-20 17:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('matchmaking', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('fb_user_id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('most_recent_fb_auth_token', models.CharField(max_length=300)),
                ('name', models.CharField(max_length=200, null=True)),
                ('age', models.IntegerField(null=True)),
                ('gender', models.CharField(max_length=1, null=True)),
                ('interested_in', models.CharField(max_length=1, null=True)),
                ('occupation', models.CharField(max_length=200, null=True)),
                ('education', models.CharField(max_length=200, null=True)),
                ('about', models.CharField(max_length=500, null=True)),
                ('min_age_preference', models.IntegerField(default=18)),
                ('max_age_preference', models.IntegerField(default=35)),
                ('max_price', models.IntegerField(default=2)),
                ('search_radius', models.IntegerField(default=24)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=13, null=True)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=13, null=True)),
                ('likes_drinks', models.NullBooleanField(default=False)),
                ('likes_food', models.NullBooleanField(default=False)),
                ('likes_coffee', models.NullBooleanField(default=False)),
                ('likes_nature', models.NullBooleanField(default=False)),
                ('likes_culture', models.NullBooleanField(default=False)),
                ('likes_active', models.NullBooleanField(default=False)),
                ('sunday_start_time', models.TimeField(blank=True, null=True)),
                ('sunday_end_time', models.TimeField(blank=True, null=True)),
                ('monday_start_time', models.TimeField(blank=True, null=True)),
                ('monday_end_time', models.TimeField(blank=True, null=True)),
                ('tuesday_start_time', models.TimeField(blank=True, null=True)),
                ('tuesday_end_time', models.TimeField(blank=True, null=True)),
                ('wednesday_start_time', models.TimeField(blank=True, null=True)),
                ('wednesday_end_time', models.TimeField(blank=True, null=True)),
                ('thursday_start_time', models.TimeField(blank=True, null=True)),
                ('thursday_end_time', models.TimeField(blank=True, null=True)),
                ('friday_start_time', models.TimeField(blank=True, null=True)),
                ('friday_end_time', models.TimeField(blank=True, null=True)),
                ('saturday_start_time', models.TimeField(blank=True, null=True)),
                ('saturday_end_time', models.TimeField(blank=True, null=True)),
                ('picture1_portrait_url', models.URLField(null=True)),
                ('picture1_square_url', models.URLField(null=True)),
                ('picture2_portrait_url', models.URLField(null=True)),
                ('picture2_square_url', models.URLField(null=True)),
                ('picture3_portrait_url', models.URLField(null=True)),
                ('picture3_square_url', models.URLField(null=True)),
                ('picture4_portrait_url', models.URLField(null=True)),
                ('picture4_square_url', models.URLField(null=True)),
                ('picture5_portrait_url', models.URLField(null=True)),
                ('picture5_square_url', models.URLField(null=True)),
                ('picture6_portrait_url', models.URLField(null=True)),
                ('picture6_square_url', models.URLField(null=True)),
                ('new_likes_notification', models.BooleanField(default=True)),
                ('new_matches_notification', models.BooleanField(default=True)),
                ('new_messages_notification', models.BooleanField(default=True)),
                ('upcoming_dates_notification', models.BooleanField(default=True)),
                ('passed_matches', models.ManyToManyField(related_name='_user_passed_matches_+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BlockedReports',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_content', models.CharField(max_length=10000)),
                ('associated_date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='associated_date', to='matchmaking.Date')),
                ('blocked_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_user', to=settings.AUTH_USER_MODEL)),
                ('blocking_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocking_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
