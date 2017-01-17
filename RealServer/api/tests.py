from django.test import TestCase, Client
from api.auth import AuthenticationBackend
from api.models import User, SexualPreference, Gender
from api.tasks import notifyUserPassedOn
from matchmaking.models import Date, DateStatus, DateCategories
from rest_framework.authtoken.models import Token
from django.utils import dateparse, timezone
from datetime import time, datetime, timedelta
import json
import pytz
from RealServer import settings


# Create your tests here.
class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.fb_user_id = "131453847271362"
        self.fb_auth_token = "EAACEFGIZCorABANb4jkcIiUKSLfXGKU15TRrQ6yRyTXZBT4MeD2l0M3eMJ6E86aoJ1149vL5E7ZAtVAisipCOQH7E5UN9XuAhSIaWnpZCJe9ZApmC0AZBFXkZA6ZC1U7uI8j9WpfCGs0qnmFUkbYKy1vDO83jiAIZCWwuqn5CUwc3tOAG2xKucDN3"
        self.auth_backend = AuthenticationBackend()
    def test_fb_auth_token_first_time_login(self):
        authenticated_user = self.auth_backend.authenticate(fb_user_id=self.fb_user_id, fb_auth_token=self.fb_auth_token)
        self.assertEqual(authenticated_user.fb_user_id, self.fb_user_id)
        self.assertEqual(authenticated_user.most_recent_fb_auth_token, self.fb_auth_token)
        self.assertTrue(Token.objects.filter(user=authenticated_user).exists())
        authenticated_user.delete()
    def test_fb_auth_token_user_already_exists(self):
        old_fb_auth_token = "FBBCEFGIZCorABANb4jkcIiUKSLfXGKU15TRrQ6yRyTXZBT4MeD2l0M3eMJ6E86aoJ1149vL5E7ZAtVAisipCOQH7E5UN9XuAhSIaWnpZCJe9ZApmC0AZBFXkZA6ZC1U7uI8j9WpfCGs0qnmFUkbYKy1vDO83jiAIZCWwuqn5CUwc3tOAG2xKucDN3"
        user = User.objects.create(fb_user_id=self.fb_user_id, most_recent_fb_auth_token=old_fb_auth_token)
        authenticated_user = self.auth_backend.authenticate(fb_user_id=self.fb_user_id,
                                                                fb_auth_token=self.fb_auth_token)
        self.assertEqual(authenticated_user.fb_user_id, self.fb_user_id)
        self.assertEqual(authenticated_user.most_recent_fb_auth_token, self.fb_auth_token)
        self.assertEqual(user, authenticated_user)
    def test_bad_auth_token(self):
        bad_fb_auth_token = "BADCEFGIZCorABANb4jkcIiUKSLfXGKU15TRrQ6yRyTXZBT4MeD2l0M3eMJ6E86aoJ1149vL5E7ZAtVAisipCOQH7E5UN9XuAhSIaWnpZCJe9ZApmC0AZBFXkZA6ZC1U7uI8j9WpfCGs0qnmFUkbYKy1vDO83jiAIZCWwuqn5CUwc3tOAG2xKucDN3"
        authenticated_user = self.auth_backend.authenticate(fb_user_id=self.fb_user_id, fb_auth_token=bad_fb_auth_token)
        self.assertEqual(authenticated_user, None)
    def test_real_auth_token_login(self):
        authenticated_user = self.auth_backend.authenticate(fb_user_id=self.fb_user_id,
                                                            fb_auth_token=self.fb_auth_token)
        token = Token.objects.get(user=authenticated_user)
        login_test_user = self.auth_backend.authenticate(fb_user_id=authenticated_user.fb_user_id,
                                                         real_auth_token=token.key)
        self.assertEqual(authenticated_user, login_test_user)
    def test_real_auth_token_login_fail(self):
        authenticated_user = self.auth_backend.authenticate(fb_user_id=self.fb_user_id,
                                                            fb_auth_token=self.fb_auth_token)
        bad_real_auth_token = 'aaaaaaaaaaaaaaaaaaa'
        authenticated_user = self.auth_backend.authenticate(fb_user_id=authenticated_user.fb_user_id,
                                                            real_auth_token=bad_real_auth_token)
        self.assertEqual(authenticated_user, None)

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(fb_user_id='131453847271362',
                                        most_recent_fb_auth_token="EAACEFGIZCorABANb4jkcIiUKSLfXGKU15TRrQ6yRyTXZBT4MeD2l0M3eMJ6E86aoJ1149vL5E7ZAtVAisipCOQH7E5UN9XuAhSIaWnpZCJe9ZApmC0AZBFXkZA6ZC1U7uI8j9WpfCGs0qnmFUkbYKy1vDO83jiAIZCWwuqn5CUwc3tOAG2xKucDN3")
        self.real_auth_token = Token.objects.create(user=self.user)
        self.c = Client()

    #TODO: Implement this test once we have a functioning test user
    def test_create_user(self):
        pass

    def test_get_user(self):
        self.user.interested_in = SexualPreference.WOMEN.value
        self.user.occupation = 'Lawyer'
        self.user.name = 'Chad Potter'
        self.user.age = 28
        self.user.gender = Gender.MAN.value
        self.user.education = 'Common University'
        self.user.save()
        response = self.c.get('/users/'+self.user.fb_user_id+'?real_auth_token='+self.real_auth_token.key,
                              HTTP_HOST = 'www.getrealdating.com')
        response = json.loads(response.content)
        self.assertEqual(response['name'], self.user.name)
        self.assertEqual(response['interested_in'], self.user.interested_in)
        self.assertEqual(response['occupation'], self.user.occupation)
        self.assertEqual(response['age'], self.user.age)
        self.assertEqual(response['gender'], self.user.gender)
        self.assertEqual(response['education'], self.user.education)
        self.assertEqual('www.getrealdating.com/media/131453847271362/picture1.jpg', response['profile_picture'])

    def test_patch_user(self):

        # Test request from Places screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "likes_drinks": True,
            "likes_food": False,
            "likes_coffee": True,
            "likes_nature": True,
            "likes_culture": True,
            "likes_active": True
        }
        response = self.c.patch('/users/'+self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.likes_drinks, True)
        self.assertEqual(load_user.likes_food, False)
        self.assertEqual(load_user.likes_coffee, True)
        self.assertEqual(load_user.likes_nature, True)
        self.assertEqual(load_user.likes_culture, True)
        self.assertEqual(load_user.likes_active, True)

        # Test request update from Places screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "likes_drinks": False,
            "likes_food": True,
            "likes_coffee": False,
            "likes_nature": True,
            "likes_culture": True,
            "likes_active": True
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.likes_drinks, False)
        self.assertEqual(load_user.likes_food, True)
        self.assertEqual(load_user.likes_coffee, False)
        self.assertEqual(load_user.likes_nature, True)
        self.assertEqual(load_user.likes_culture, True)
        self.assertEqual(load_user.likes_active, True)

        # Test request from Time input screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "sunday_start_time": time(hour=16, minute=30).isoformat(),
            "sunday_end_time": time(hour=18, minute=30).isoformat(),
            "monday_start_time": time(hour=14, minute=0).isoformat(),
            "monday_end_time": time(hour=20, minute=0).isoformat(),
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.sunday_start_time, dateparse.parse_time(data["sunday_start_time"]))
        self.assertEqual(load_user.sunday_end_time, dateparse.parse_time(data["sunday_end_time"]))
        self.assertEqual(load_user.monday_start_time, dateparse.parse_time(data["monday_start_time"]))
        self.assertEqual(load_user.monday_end_time, dateparse.parse_time(data["monday_end_time"]))

        # Test request update from Time input screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "sunday_start_time": time(hour=17, minute=30).isoformat(),
            "sunday_end_time": time(hour=19, minute=30).isoformat(),
            "monday_start_time": time(hour=10, minute=0).isoformat(),
            "monday_end_time": time(hour=21, minute=0).isoformat(),
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.sunday_start_time, dateparse.parse_time(data["sunday_start_time"]))
        self.assertEqual(load_user.sunday_end_time, dateparse.parse_time(data["sunday_end_time"]))
        self.assertEqual(load_user.monday_start_time, dateparse.parse_time(data["monday_start_time"]))
        self.assertEqual(load_user.monday_end_time, dateparse.parse_time(data["monday_end_time"]))

class DateTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(fb_user_id='122700428234141',
                                         most_recent_fb_auth_token='EAACEFGIZCorABABwneNGNfqZAmeQI2QlftiHN7gkf2Ok4kJaZCbOo10XbD3wZAeaOFzYVaZBYOPoLPoF3VpygpZAZAOmOJbRgfp09h7Wp1g5vIpsZAuVpqVu3k8lYXkt6GJgCPsH43hecd7o8TueBOxt9lZAgWcyoCRuBjhLZBl5WBFvMW3RhQS5VohkYzTJgpQDGDHMM8t3oNjAZDZD')
        self.user2 = User.objects.create(fb_user_id='116474138858424',
                                         most_recent_fb_auth_token='EAACEFGIZCorABADEzDQtokRhCZCv7jFt6mXCvZCXxwNiNL58sM9rHD6raZCcSTQfDkkEEr2X7MbwxrwLMU6ypLg3Or8XyfG1ezAvZCYpGL4CubswaZCn7ZBvEePLCcDhZBYe3Gzq6qhqEPKQNLvRKB43VtwC5jrpG4KzDz2i9seXfrMZBhCsoHf40dhPl9M3r54tAxxP64Ge90wZDZD')
        self.real_auth_token1 = Token.objects.create(user=self.user1)
        self.real_auth_token2 = Token.objects.create(user=self.user2)
        self.c = Client()
        settings.CELERY_ALWAYS_EAGER = True
    def test_date_patch(self):
        # Test both users like each other
        date = Date(user1=self.user1, user2=self.user2, expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0, tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date.original_expires_at = date.expires_at
        date.user2_likes = DateStatus.LIKES.value
        date.save()
        data = {
            "real_auth_token": self.real_auth_token1.key,
            "status": DateStatus.LIKES.value
        }
        response = self.c.patch('/users/'+ self.user1.fb_user_id + '/dates/'+ str(date.pk), json.dumps(data))
        date = Date.objects.get(pk=date.pk)
        self.assertEqual(date.expires_at, datetime(year=2017, month=1, day=20, hour=23, minute=59, tzinfo=pytz.UTC))

        # Test user 1 likes, user 2 undecided
        date = Date(user1=self.user1, user2=self.user2,
                    expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                        tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date.original_expires_at = date.expires_at
        date.user2_likes = DateStatus.UNDECIDED.value
        date.save()
        data = {
            "real_auth_token": self.real_auth_token1.key,
            "status": DateStatus.LIKES.value
        }
        response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
        date = Date.objects.get(pk=date.pk)
        self.assertEqual(date.expires_at.replace(minute=0, second=0, microsecond=0),
                         (timezone.now() + timedelta(hours=24)).replace(minute=0, second=0, microsecond=0))

        # Test user 1 likes, user 2 passed
        date = Date(user1=self.user1, user2=self.user2,
                    expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                        tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date.original_expires_at = date.expires_at
        date.user2_likes = DateStatus.PASS.value
        date.save()
        data = {
            "real_auth_token": self.real_auth_token1.key,
            "status": DateStatus.LIKES.value
        }
        response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
        date = Date.objects.get(pk=date.pk)
        self.assertEqual(date.expires_at.replace(minute=0, second=0, microsecond=0),
                         (timezone.now() + timedelta(hours=24)).replace(minute=0, second=0, microsecond=0))
        notifyUserPassedOn(user1_id=self.user1.fb_user_id, user2_id=self.user2.fb_user_id, date_id=date.pk)
        date = Date.objects.get(pk=date.pk)
        self.assertEqual(date.expires_at, date.original_expires_at)

