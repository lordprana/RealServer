import json
from datetime import time, datetime, timedelta
from datetime import date as dt_date
import os

import pytz
import mock
from django.test import TestCase, Client
from django.utils import dateparse, timezone
from rest_framework.authtoken.models import Token

from RealServer import settings
from api.auth import AuthenticationBackend
from api.hardcoded_dates import getHardcodedDates
from api.models import User, SexualPreference, Gender, BlockedReports, Status, FCMDevice
from api.tasks import notifyUserPassedOn
from matchmaking.models import Date, DateStatus, DateCategories


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
        self.c = Client()

    def test_create_user(self):
        os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAI4755USWAQYAFTUA'
        os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
        os.environ['S3_BUCKET'] = 'realdatingbucket'
        fb_user_id = '2959531196950'
        fb_auth_token = 'EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum'
        data = {
            'fb_user_id': fb_user_id,
            'fb_auth_token': fb_auth_token
        }
        self.assertEqual(User.objects.all().count(), 0)
        self.assertEqual(Token.objects.all().count(), 0)
        print("In tests")
        response = self.c.post('/users', data=json.dumps(data), content_type='application/json')
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(Token.objects.all().count(), 1)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['real_auth_token'], Token.objects.first().key)
        self.assertEqual(response_json['fb_user_id'], User.objects.first().fb_user_id)
        self.assertEqual(response_json['status'], Status.NEW_USER.value)
        user = User.objects.first()
        self.assertEqual(user.first_name, 'Matthew')
        self.assertEqual(user.last_name, 'Gaba')
        self.assertEqual(user.gender, Gender.MAN.value)
        self.assertEqual(user.education, 'Yale University')
        self.assertEqual(user.occupation, 'Certified Yoga & Meditation Teacher')
        self.assertEqual(user.age, 27)
        self.assertEqual(user.interested_in, SexualPreference.WOMEN.value)
        self.assertTrue('realdatingbucket.s3.amazonaws.com' in user.picture1_square_url)
        self.assertTrue('realdatingbucket.s3.amazonaws.com' in user.picture1_portrait_url)

    def test_get_user(self):
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token = Token.objects.create(user=self.user)
        self.user.interested_in = SexualPreference.WOMEN.value
        self.user.occupation = 'Lawyer'
        self.user.first_name = 'Chad'
        self.user.age = 28
        self.user.gender = Gender.MAN.value
        self.user.education = 'Common University'
        self.user.picture1_portrait_url = 'https://s3.amazonaws.com/realdatingbucket/2959531196950/ataxfmkygcul'
        self.user.picture1_square_url = 'https://s3.amazonaws.com/realdatingbucket/2959531196950/auxmmsssuhmt'
        self.user.save()
        response = self.c.get('/users/'+self.user.fb_user_id+'?real_auth_token='+self.real_auth_token.key)
        response = json.loads(response.content)
        self.assertEqual(response['name'], self.user.first_name)
        self.assertEqual(response['interested_in'], self.user.interested_in)
        self.assertEqual(response['occupation'], self.user.occupation)
        self.assertEqual(response['age'], self.user.age)
        self.assertEqual(response['gender'], self.user.gender)
        self.assertEqual(response['education'], self.user.education)
        self.assertEqual(response['picture1_portrait_url'], self.user.picture1_portrait_url)
        self.assertEqual(response['picture1_square_url'], self.user.picture1_square_url)
        self.assertEqual(response['picture2_portrait_url'], None)
        self.assertEqual(response['picture2_square_url'], None)

    def test_get_time_preferences(self):
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token = Token.objects.create(user=self.user)
        self.user.sun_start_time = time(hour=8)
        self.user.sun_end_time = time(hour=23)
        self.user.mon_start_time = time(hour=8)
        self.user.mon_end_time = time(hour=23)
        self.user.tue_start_time = time(hour=8)
        self.user.tue_end_time = time(hour=23)
        self.user.wed_start_time = time(hour=8)
        self.user.wed_end_time = time(hour=23)
        self.user.thur_start_time = time(hour=8)
        self.user.thur_end_time = time(hour=23)
        self.user.fri_start_time = time(hour=8)
        self.user.fri_end_time = time(hour=23)
        self.user.sat_start_time = time(hour=8)
        self.user.sat_end_time = time(hour=23)
        self.user.save()
        response = self.c.get('/users/' + self.user.fb_user_id + '/time_preferences?real_auth_token=' + self.real_auth_token.key)
        response = json.loads(response.content)
        self.assertEqual(response['sun_start_time'], self.user.sun_start_time.isoformat())
        self.assertEqual(response['sun_end_time'], self.user.sun_end_time.isoformat())
        self.assertEqual(response['mon_start_time'], self.user.mon_start_time.isoformat())
        self.assertEqual(response['mon_end_time'], self.user.mon_end_time.isoformat())
        self.assertEqual(response['tue_start_time'], self.user.tue_start_time.isoformat())
        self.assertEqual(response['tue_end_time'], self.user.tue_end_time.isoformat())
        self.assertEqual(response['wed_start_time'], self.user.wed_start_time.isoformat())
        self.assertEqual(response['wed_end_time'], self.user.wed_end_time.isoformat())
        self.assertEqual(response['thur_start_time'], self.user.thur_start_time.isoformat())
        self.assertEqual(response['thur_end_time'], self.user.thur_end_time.isoformat())
        self.assertEqual(response['fri_start_time'], self.user.fri_start_time.isoformat())
        self.assertEqual(response['fri_end_time'], self.user.fri_end_time.isoformat())
        self.assertEqual(response['sat_start_time'], self.user.sat_start_time.isoformat())
        self.assertEqual(response['sat_end_time'], self.user.sat_end_time.isoformat())

    def test_get_place_preferences(self):
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token = Token.objects.create(user=self.user)
        self.user.likes_drinks = True
        self.user.likes_food = True
        self.user.likes_coffee = True
        self.user.likes_parks = True
        self.user.likes_museums = True
        self.user.likes_fun = True
        self.user.save()
        response = self.c.get('/users/' + self.user.fb_user_id + '/place_preferences?real_auth_token=' + self.real_auth_token.key)
        response = json.loads(response.content)
        self.assertEqual(response['likes_drinks'], self.user.likes_drinks)
        self.assertEqual(response['likes_food'], self.user.likes_food)
        self.assertEqual(response['likes_coffee'], self.user.likes_coffee)
        self.assertEqual(response['likes_parks'], self.user.likes_parks)
        self.assertEqual(response['likes_museums'], self.user.likes_museums)
        self.assertEqual(response['likes_fun'], self.user.likes_fun)

    def test_registration_city(self):
        self.user1 = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token1 = Token.objects.create(user=self.user1)
        # Test user1 registers in New York
        data = {
            "real_auth_token": self.real_auth_token1.key,
            "latitude": 40.8,
            "longitude": -73.95
        }
        response = self.c.patch('/users/' + self.user1.fb_user_id, json.dumps(data))
        self.user1 = User.objects.get(pk=self.user1.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.registration_city, "New York")
        self.assertEqual(self.user1.registration_state, "New York")
        self.assertEqual(self.user1.search_radius, 3)

        # Test user1 moves to Dallas and makes request (city and state should remain New York)
        data = {
            "real_auth_token": self.real_auth_token1.key,
            "latitude": 32.88,
            "longitude": -96.76
        }
        response = self.c.patch('/users/' + self.user1.fb_user_id, json.dumps(data))
        self.user1 = User.objects.get(pk=self.user1.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.registration_city, "New York")
        self.assertEqual(self.user1.registration_state, "New York")
        self.assertEqual(self.user1.search_radius, 3)

        # Test user2 registers in Dallas
        self.user2 = User.objects.create(fb_user_id='2959531196951',
                                         most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token2 = Token.objects.create(user=self.user2)
        data = {
            "real_auth_token": self.real_auth_token2.key,
            "latitude": 32.88,
            "longitude": -96.76
        }
        response = self.c.patch('/users/' + self.user2.fb_user_id, json.dumps(data))
        self.user2 = User.objects.get(pk=self.user2.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user2.registration_city, "Dallas")
        self.assertEqual(self.user2.registration_state, "Texas")
        self.assertEqual(self.user2.search_radius, 10)

    def test_patch_user(self):
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.user.picture1_portrait_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/aytsnqnjcfqb'
        self.user.picture1_square_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/bortmirwuvzt'
        self.user.picture2_portrait_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/bqxkwoyqbawa'
        self.user.picture2_square_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/cosipwzcfziu'
        self.user.picture3_portrait_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/ecxijzcbecrz'
        self.user.picture3_square_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/egcuuluxxigq'
        self.user.picture4_portrait_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/ghruwyjeicpv' # Is deleted in test
        self.user.picture4_square_url = 'https://realdatingbucket.s3.amazonaws.com/2959531196950/gobquxnbgodb' # Is deleted in test
        self.user.save()
        self.real_auth_token = Token.objects.create(user=self.user)

        # Test request from Places screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "likes_drinks": True,
            "likes_food": False,
            "likes_coffee": True,
            "likes_parks": True,
            "likes_museums": True,
            "likes_fun": True
        }
        response = self.c.patch('/users/'+self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.likes_drinks, True)
        self.assertEqual(load_user.likes_food, False)
        self.assertEqual(load_user.likes_coffee, True)
        self.assertEqual(load_user.likes_parks, True)
        self.assertEqual(load_user.likes_museums, True)
        self.assertEqual(load_user.likes_fun, True)

        # Test request update from Places screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "likes_drinks": False,
            "likes_food": True,
            "likes_coffee": False,
            "likes_parks": True,
            "likes_museums": True,
            "likes_fun": True
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.likes_drinks, False)
        self.assertEqual(load_user.likes_food, True)
        self.assertEqual(load_user.likes_coffee, False)
        self.assertEqual(load_user.likes_parks, True)
        self.assertEqual(load_user.likes_museums, True)
        self.assertEqual(load_user.likes_fun, True)

        # Test request from Time input screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "sun_start_time": time(hour=16, minute=30).isoformat(),
            "sun_end_time": time(hour=18, minute=30).isoformat(),
            "mon_start_time": time(hour=14, minute=0).isoformat(),
            "mon_end_time": time(hour=20, minute=0).isoformat(),
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.sun_start_time, dateparse.parse_time(data["sun_start_time"]))
        self.assertEqual(load_user.sun_end_time, dateparse.parse_time(data["sun_end_time"]))
        self.assertEqual(load_user.mon_start_time, dateparse.parse_time(data["mon_start_time"]))
        self.assertEqual(load_user.mon_end_time, dateparse.parse_time(data["mon_end_time"]))

        # Test request from Time input screen when user is simply updating and not creating new values
        data = {
            "real_auth_token": self.real_auth_token.key,
            "sun_start_time": time(hour=17, minute=30).isoformat(),
            "sun_end_time": time(hour=19, minute=30).isoformat(),
            "mon_start_time": time(hour=10, minute=0).isoformat(),
            "mon_end_time": time(hour=21, minute=0).isoformat(),
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.sun_start_time, dateparse.parse_time(data["sun_start_time"]))
        self.assertEqual(load_user.sun_end_time, dateparse.parse_time(data["sun_end_time"]))
        self.assertEqual(load_user.mon_start_time, dateparse.parse_time(data["mon_start_time"]))
        self.assertEqual(load_user.mon_end_time, dateparse.parse_time(data["mon_end_time"]))

        # Test request from setup profile screen
        data = {
            "real_auth_token": self.real_auth_token.key,
            "interested_in": SexualPreference.BISEXUAL.value,
            "occupation": "Plumber",
            "education": None,
            "about": "I love women and men."
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.interested_in, data["interested_in"])
        self.assertEqual(load_user.occupation, data["occupation"])
        self.assertEqual(load_user.education, data["education"])
        self.assertEqual(load_user.about, data["about"])
        self.assertEqual(load_user.status, Status.FINISHED_PROFILE.value)

        # Test new picture patch. Requires manual verification on S3 that files were deleted
        os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAI4755USWAQYAFTUA'
        os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
        os.environ['S3_BUCKET'] = 'realdatingbucket'
        data = {
            'real_auth_token': self.real_auth_token.key,
            'picture1_portrait_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/aytsnqnjcfqb',
            'picture1_square_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/bortmirwuvzt',
            'picture2_portrait_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/ecxijzcbecrz',
            'picture2_square_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/egcuuluxxigq',
            'picture3_portrait_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/bqxkwoyqbawa',
            'picture3_square_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/cosipwzcfziu',
            'picture4_portrait_url': None,
            'picture4_square_url': None
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.picture1_portrait_url, data['picture1_portrait_url'])
        self.assertEqual(load_user.picture1_square_url, data['picture1_square_url'])
        self.assertEqual(load_user.picture2_portrait_url, data['picture2_portrait_url'])
        self.assertEqual(load_user.picture2_square_url, data['picture2_square_url'])
        self.assertEqual(load_user.picture3_portrait_url, data['picture3_portrait_url'])
        self.assertEqual(load_user.picture3_square_url, data['picture3_square_url'])
        self.assertEqual(load_user.picture4_portrait_url, data['picture4_portrait_url'])
        self.assertEqual(load_user.picture4_square_url, data['picture4_square_url'])

        # Test new picture patch when there are no values for picture already in the record
        load_user.picture1_portrait_url = None
        load_user.picture1_square_url = None
        load_user.picture2_portrait_url = None
        load_user.picture2_square_url = None
        load_user.picture3_portrait_url = None
        load_user.picture3_square_url = None
        load_user.picture4_portrait_url = None
        load_user.picture4_square_url = None
        load_user.save()

        data = {
            'real_auth_token': self.real_auth_token.key,
            'picture1_portrait_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/qfmcexuipbue',
            'picture1_square_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/rgifzhzprsmn',
            'picture2_portrait_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/ozduryavtrza',
            'picture2_square_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/pqnwvwggyqoa',
            'picture3_portrait_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/vpdyrbyeitwt',
            'picture3_square_url': 'https://realdatingbucket.s3.amazonaws.com/2959531196950/wchmoijakryx',
            'picture4_portrait_url': None,
            'picture4_square_url': None
        }
        response = self.c.patch('/users/' + self.user.fb_user_id, json.dumps(data))
        load_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_user.picture1_portrait_url, data['picture1_portrait_url'])
        self.assertEqual(load_user.picture1_square_url, data['picture1_square_url'])
        self.assertEqual(load_user.picture2_portrait_url, data['picture2_portrait_url'])
        self.assertEqual(load_user.picture2_square_url, data['picture2_square_url'])
        self.assertEqual(load_user.picture3_portrait_url, data['picture3_portrait_url'])
        self.assertEqual(load_user.picture3_square_url, data['picture3_square_url'])
        self.assertEqual(load_user.picture4_portrait_url, data['picture4_portrait_url'])
        self.assertEqual(load_user.picture4_square_url, data['picture4_square_url'])


    def test_register_device(self):
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token = Token.objects.create(user=self.user)
        registration_token = 'abiud9325107852nvczhj4'
        data = {
            'real_auth_token': self.real_auth_token.key,
            'registration_token': registration_token
        }
        response = self.c.put('/users/' + self.user.fb_user_id + '/register_device/', json.dumps(data), content_type='application/json')
        device = FCMDevice.objects.get(registration_token=registration_token, user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(device, None)

    def test_sign_s3(self):
        os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAI4755USWAQYAFTUA'
        os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
        os.environ['S3_BUCKET'] = 'realdatingbucket'
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token = Token.objects.create(user=self.user)
        file_type = 'jpeg'
        response = self.c.get('/users/' + self.user.fb_user_id + '/sign_s3?' + 'real_auth_token=' +
                              self.real_auth_token.key + '&file_type=' + file_type)
        json_response = json.loads(response.content)
        self.assertTrue(('https://realdatingbucket.s3.amazonaws.com/' + self.user.fb_user_id) in json_response['url'])
        self.assertEqual(json_response['data']['url'], 'https://realdatingbucket.s3.amazonaws.com/')
        self.assertEqual(json_response['data']['fields']['AWSAccessKeyId'], os.environ['AWS_ACCESS_KEY_ID'])

    def test_settings(self):
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token = Token.objects.create(user=self.user)
        response = self.c.get('/users/' + self.user.fb_user_id + '/settings?' + 'real_auth_token=' +
                              self.real_auth_token.key)
        json_response = json.loads(response.content)
        # Check that json values equal default values specified in User model
        self.assertEqual(json_response['search_radius'], 24)
        self.assertEqual(json_response['min_age_preference'], 18)
        self.assertEqual(json_response['max_age_preference'], 35)
        self.assertEqual(json_response['max_price'], 2)
        self.assertEqual(json_response['new_likes_notification'], True)
        self.assertEqual(json_response['new_matches_notification'], True)
        self.assertEqual(json_response['new_messages_notification'], True)
        self.assertEqual(json_response['upcoming_dates_notification'], True)

    def test_logout(self):
        self.user = User.objects.create(fb_user_id='2959531196950',
                                        most_recent_fb_auth_token="EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum")
        self.real_auth_token = Token.objects.create(user=self.user)
        self.assertNotEqual(self.user.status, Status.INACTIVE.value)
        response = self.c.get('/users/' + self.user.fb_user_id + '/logout?' + 'real_auth_token=' +
                              self.real_auth_token.key)
        self.user = User.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.status, Status.INACTIVE.value)

NOW_FOR_TESTING = datetime(year=2017, month=1, day=19, hour=22, minute=0, second=0, tzinfo=pytz.utc)
def mocked_now():
    return NOW_FOR_TESTING

class DateTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(fb_user_id='122700428234141',
                                         most_recent_fb_auth_token='EAACEFGIZCorABABwneNGNfqZAmeQI2QlftiHN7gkf2Ok4kJaZCbOo10XbD3wZAeaOFzYVaZBYOPoLPoF3VpygpZAZAOmOJbRgfp09h7Wp1g5vIpsZAuVpqVu3k8lYXkt6GJgCPsH43hecd7o8TueBOxt9lZAgWcyoCRuBjhLZBl5WBFvMW3RhQS5VohkYzTJgpQDGDHMM8t3oNjAZDZD',
                                         timezone = 'US/Eastern', first_name = 'First')
        self.user2 = User.objects.create(fb_user_id='116474138858424',
                                         most_recent_fb_auth_token='EAACEFGIZCorABADEzDQtokRhCZCv7jFt6mXCvZCXxwNiNL58sM9rHD6raZCcSTQfDkkEEr2X7MbwxrwLMU6ypLg3Or8XyfG1ezAvZCYpGL4CubswaZCn7ZBvEePLCcDhZBYe3Gzq6qhqEPKQNLvRKB43VtwC5jrpG4KzDz2i9seXfrMZBhCsoHf40dhPl9M3r54tAxxP64Ge90wZDZD',
                                         timezone = 'US/Eastern', first_name= 'First')
        self.real_auth_token1 = Token.objects.create(user=self.user1)
        self.real_auth_token2 = Token.objects.create(user=self.user2)
        self.c = Client()
    def test_date_patch_status(self):
        # Test both users like each other
        date = Date(user1=self.user1, user2=self.user2, expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0, tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value, date_of_date=dt_date(year=2017,month=1, day=20))
        date.original_expires_at = date.expires_at
        date.user2_likes = DateStatus.LIKES.value
        date.save()
        data = {
            "real_auth_token": self.real_auth_token1.key,
            "status": DateStatus.LIKES.value
        }
        response = self.c.patch('/users/'+ self.user1.fb_user_id + '/dates/'+ str(date.pk), json.dumps(data))
        date = Date.objects.get(pk=date.pk)
        self.assertEqual(date.expires_at, datetime(year=2017, month=1, day=21, hour=4, minute=59, tzinfo=pytz.UTC))

        # Test user 1 likes, user 2 undecided with date occuring less than a day away
        with mock.patch('django.utils.timezone.now', side_effect=mocked_now):
            date = Date(user1=self.user1, user2=self.user2,
                        expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                            tzinfo=pytz.UTC),
                        day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                        category=DateCategories.COFFEE.value, date_of_date=dt_date(year=2017,month=1, day=20))
            date.original_expires_at = date.expires_at
            date.user2_likes = DateStatus.UNDECIDED.value
            date.save()
            data = {
                "real_auth_token": self.real_auth_token1.key,
                "status": DateStatus.LIKES.value
            }
            response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
            date = Date.objects.get(pk=date.pk)
            self.assertEqual(date.expires_at.replace(second=0, microsecond=0),
                             datetime(year=2017, month=1, day=20, hour=17, minute=30, tzinfo=pytz.utc))

            # Test user 1 likes, user 2 undecided with date occuring more than a day away
            with mock.patch('django.utils.timezone.now', side_effect=mocked_now):
                date = Date(user1=self.user1, user2=self.user2,
                            expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                                tzinfo=pytz.UTC),
                            day='sat', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                            category=DateCategories.COFFEE.value, date_of_date=dt_date(year=2017, month=1, day=21))
                date.original_expires_at = date.expires_at
                date.user2_likes = DateStatus.UNDECIDED.value
                date.save()
                data = {
                    "real_auth_token": self.real_auth_token1.key,
                    "status": DateStatus.LIKES.value
                }
                response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
                date = Date.objects.get(pk=date.pk)
                self.assertEqual(date.expires_at.replace(second=0, microsecond=0),
                                 timezone.now() + timedelta(hours=24))

        # Test user 1 likes, user 2 passed with date occuring less than a day away
        with mock.patch('django.utils.timezone.now', side_effect=mocked_now):
            date = Date(user1=self.user1, user2=self.user2,
                        expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                            tzinfo=pytz.UTC),
                        day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                        category=DateCategories.COFFEE.value, date_of_date=dt_date(year=2017,month=1, day=20))
            date.original_expires_at = date.expires_at
            date.user2_likes = DateStatus.PASS.value
            date.save()
            data = {
                "real_auth_token": self.real_auth_token1.key,
                "status": DateStatus.LIKES.value
            }
            response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
            date = Date.objects.get(pk=date.pk)
            self.assertEqual(date.expires_at.replace(second=0, microsecond=0),
                             datetime(year=2017, month=1, day=20, hour=17, minute=30, tzinfo=pytz.utc))
            notifyUserPassedOn(user1_id=self.user1.fb_user_id, user2_id=self.user2.fb_user_id, date_id=date.pk)
            date = Date.objects.get(pk=date.pk)
            self.assertEqual(date.expires_at, date.original_expires_at)

        # Test user 1 likes, user 2 passed with date occuring more than a day away
        with mock.patch('django.utils.timezone.now', side_effect=mocked_now):
            date = Date(user1=self.user1, user2=self.user2,
                        expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                            tzinfo=pytz.UTC),
                        day='sat', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                        category=DateCategories.COFFEE.value, date_of_date=dt_date(year=2017, month=1, day=21))
            date.original_expires_at = date.expires_at
            date.user2_likes = DateStatus.PASS.value
            date.save()
            data = {
                "real_auth_token": self.real_auth_token1.key,
                "status": DateStatus.LIKES.value
            }
            response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
            date = Date.objects.get(pk=date.pk)
            self.assertEqual(date.expires_at.replace(second=0, microsecond=0),
                             timezone.now() + timedelta(hours=24))
            notifyUserPassedOn(user1_id=self.user1.fb_user_id, user2_id=self.user2.fb_user_id, date_id=date.pk)
            date = Date.objects.get(pk=date.pk)
            self.assertEqual(date.expires_at, date.original_expires_at)

        # Test user 1 passed, user 2 undecided
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
            "status": DateStatus.PASS.value
        }
        response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
        self.user1 = User.objects.get(pk=self.user1.pk)
        self.assertEqual(self.user1.passed_matches.all().count(), 1)

    def test_date_by_date_id(self):
        date = Date(user1=self.user1, user2=self.user2,
                    expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                        tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date.original_expires_at = date.expires_at
        date.save()
        response = self.c.get('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk) + '?real_auth_token=' + self.real_auth_token1.key)
        self.assertEqual(json.loads(response.content)['date_id'], date.pk)

    def test_date_patch_inspected_match(self):
        # Test user 1 inspects user 2
        date = Date(user1=self.user1, user2=self.user2,
                    expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                        tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date.original_expires_at = date.expires_at
        date.user2_likes = DateStatus.LIKES.value
        date.save()
        data = {
            "real_auth_token": self.real_auth_token1.key,
            "inspected_match": True
        }
        response = self.c.patch('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk), json.dumps(data))
        date = Date.objects.get(pk=date.pk)
        self.assertEqual(date.inspected_match, True)

    def test_past_dates(self):
        date1 = Date(user1=self.user1, user2=self.user2,
                    expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                        tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date1.original_expires_at = date1.expires_at
        date1.user1_likes = DateStatus.LIKES.value
        date1.user2_likes = DateStatus.LIKES.value
        date1.date_of_date = timezone.now().date() - timedelta(days=2)
        date1.save()
        date2 = Date(user1=self.user1, user2=self.user2,
                     expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                         tzinfo=pytz.UTC),
                     day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                     category=DateCategories.COFFEE.value)
        date2.original_expires_at = date2.expires_at
        date2.user1_likes = DateStatus.LIKES.value
        date2.user2_likes = DateStatus.LIKES.value
        date2.date_of_date = timezone.now().date() - timedelta(days=7)
        date2.save()
        response = self.c.get('/users/' + self.user1.fb_user_id + '/past_dates?real_auth_token=' + self.real_auth_token1.key)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json), 2)
        self.assertEqual(response_json[0]['date_id'], 1)
        self.assertEqual(response_json[1]['date_id'], 2)

    def test_unmatch(self):
        # Both users like each other at first
        date = Date(user1=self.user1, user2=self.user2,
                    expires_at=datetime(year=2017, month=1, day=15, hour=15, minute=12, second=0, microsecond=0,
                                        tzinfo=pytz.UTC),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date.original_expires_at = date.expires_at - timedelta(days=1)
        date.user1_likes = DateStatus.LIKES.value
        date.user2_likes = DateStatus.LIKES.value
        date.save()
        response = self.c.get('/users/' + self.user1.fb_user_id + '/dates/' + str(date.pk) + '/unmatch?real_auth_token=' + self.real_auth_token1.key)
        date = Date.objects.get(pk=date.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(date.user1_likes, DateStatus.PASS.value)
        self.assertEqual(date.user2_likes, DateStatus.PASS.value)
        self.assertEqual(date.expires_at, date.original_expires_at)
        self.assertEqual(date.user1.passed_matches.count(), 1)
        self.assertEqual(date.user2.passed_matches.count(), 1)

class ReportAndBlockTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(fb_user_id='122700428234141',
                                         most_recent_fb_auth_token='EAACEFGIZCorABABwneNGNfqZAmeQI2QlftiHN7gkf2Ok4kJaZCbOo10XbD3wZAeaOFzYVaZBYOPoLPoF3VpygpZAZAOmOJbRgfp09h7Wp1g5vIpsZAuVpqVu3k8lYXkt6GJgCPsH43hecd7o8TueBOxt9lZAgWcyoCRuBjhLZBl5WBFvMW3RhQS5VohkYzTJgpQDGDHMM8t3oNjAZDZD')
        self.user2 = User.objects.create(fb_user_id='116474138858424',
                                         most_recent_fb_auth_token='EAACEFGIZCorABADEzDQtokRhCZCv7jFt6mXCvZCXxwNiNL58sM9rHD6raZCcSTQfDkkEEr2X7MbwxrwLMU6ypLg3Or8XyfG1ezAvZCYpGL4CubswaZCn7ZBvEePLCcDhZBYe3Gzq6qhqEPKQNLvRKB43VtwC5jrpG4KzDz2i9seXfrMZBhCsoHf40dhPl9M3r54tAxxP64Ge90wZDZD')
        self.real_auth_token1 = Token.objects.create(user=self.user1)
        self.real_auth_token2 = Token.objects.create(user=self.user2)
        self.c = Client()
    def test_report_and_block(self):
        date = Date(user1=self.user1, user2=self.user2,
                    expires_at=timezone.now()+timedelta(hours=24),
                    day='fri', start_time=time(hour=18), place_id='sample-id', place_name='Sample Place',
                    category=DateCategories.COFFEE.value)
        date.original_expires_at = date.expires_at
        date.user1_likes = DateStatus.LIKES.value
        date.user2_likes = DateStatus.LIKES.value
        date.save()
        data = {
            "fb_user_id": self.user1.pk,
            "real_auth_token": self.real_auth_token1.key,
            "blocked_user_id": self.user2.pk,
            "report_content": "He was saying lewd things to me in the chat. He sent me a picture of his you know what.",
            "date_id": date.pk
        }

        response = self.c.post('/reportandblock/', data=json.dumps(data), content_type='application/json')
        date = Date.objects.get(pk=date.pk)
        report = BlockedReports.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(date.user1_likes, DateStatus.PASS.value)
        self.assertEqual(date.user2_likes, DateStatus.PASS.value)
        self.assertEqual(date.user1.passed_matches.count(), 1)
        self.assertEqual(date.user2.passed_matches.count(), 1)
        self.assertEqual(date.expires_at, date.original_expires_at)
        self.assertEqual(report.report_content, data['report_content'])
        self.assertEqual(report.blocking_user, self.user1)
        self.assertEqual(report.blocked_user, self.user2)
        self.assertEqual(report.associated_date, date)

class HardcodedDatesTestCase(TestCase):
    def test_hardcoded_dates(self):
        # This tests exists only so I can step through with debugger. Nothing is being tested
        self.user1 = User.objects.create(fb_user_id='122700428234141',
                                         most_recent_fb_auth_token='EAACEFGIZCorABABwneNGNfqZAmeQI2QlftiHN7gkf2Ok4kJaZCbOo10XbD3wZAeaOFzYVaZBYOPoLPoF3VpygpZAZAOmOJbRgfp09h7Wp1g5vIpsZAuVpqVu3k8lYXkt6GJgCPsH43hecd7o8TueBOxt9lZAgWcyoCRuBjhLZBl5WBFvMW3RhQS5VohkYzTJgpQDGDHMM8t3oNjAZDZD')
        self.user1.timezone = 'America/Chicago'
        getHardcodedDates(self.user1, 'thur')