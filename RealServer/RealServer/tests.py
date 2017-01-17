from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime
import facebook
import settings
import os
from tools import nextDayOfWeekToDatetime
from api.models import User

class FacebookTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(fb_user_id='122700428234141', most_recent_fb_auth_token='EAACEFGIZCorABABwneNGNfqZAmeQI2QlftiHN7gkf2Ok4kJaZCbOo10XbD3wZAeaOFzYVaZBYOPoLPoF3VpygpZAZAOmOJbRgfp09h7Wp1g5vIpsZAuVpqVu3k8lYXkt6GJgCPsH43hecd7o8TueBOxt9lZAgWcyoCRuBjhLZBl5WBFvMW3RhQS5VohkYzTJgpQDGDHMM8t3oNjAZDZD')
        self.user2 = User.objects.create(fb_user_id='116474138858424', most_recent_fb_auth_token='EAACEFGIZCorABADEzDQtokRhCZCv7jFt6mXCvZCXxwNiNL58sM9rHD6raZCcSTQfDkkEEr2X7MbwxrwLMU6ypLg3Or8XyfG1ezAvZCYpGL4CubswaZCn7ZBvEePLCcDhZBYe3Gzq6qhqEPKQNLvRKB43VtwC5jrpG4KzDz2i9seXfrMZBhCsoHf40dhPl9M3r54tAxxP64Ge90wZDZD')

    def test_mutual_friends(self):
        mutual_friends_json = facebook.getMutualFriends(self.user1, self.user2)
        self.assertEqual(mutual_friends_json['summary']['total_count'], 2)
        self.assertEqual(mutual_friends_json['data'][0]['name'], 'Barbara McDonaldman')

    # TODO: Test this once we have a test user with correct permissions set up
    def test_user_info(self):
        user_info_json = facebook.getUserInfo(self.user1)
        print(user_info_json)

    def test_user_profile_picture(self):
        # Test returns .jpeg if good request
        user_picture = facebook.getUserProfilePicture(self.user1)
        self.assertEqual(user_picture[:11], '\xff\xd8\xff\xe0\x00\x10JFIF\x00') # This string begins every picture returned by Facebook

        # Test returns none if bad request
        self.user1.most_recent_fb_auth_token = 'EAACE'
        self.user1.save()
        user_picture = facebook.getUserProfilePicture(self.user1)
        self.assertEqual(user_picture, None)

class ToolsTest(TestCase):
    def test_day_of_week_difference(self):
        dt = datetime(year=2017, month=1, day=16)
        dt = nextDayOfWeekToDatetime(dt, 'wed')
        self.assertEqual(dt, datetime(year=2017, month=1, day=18))
        dt = datetime(year=2017, month=1, day=16)
        dt = nextDayOfWeekToDatetime(dt, 'sun')
        self.assertEqual(dt, datetime(year=2017, month=1, day=22))
        dt = nextDayOfWeekToDatetime(dt, 'tue')
        self.assertEqual(dt, datetime(year=2017, month=1, day=24))
