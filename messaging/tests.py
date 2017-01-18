from django.test import TestCase
from django.test import Client
from api.models import User
import json

# Create your tests here.

class MessagingTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        # Create test users using users endpoint
        user1_fb_auth_token = 'EAACEFGIZCorABAGurIRI6j0ICb3dnljgOh5MZBDGZBdOYwsZC5ZAORBmZCf6OOqQLeM5Y13JqIOPNCEfrUbPQbz8V49aFSrIJO9iADV3he9eEwCmQHWQW3OZCNAXjZBXjxEqNl6ufllsW6jJM3CfthZB94WZAeZB67QObir6LuVp9r8WH2ySKF2o6z451DpjtyYcBQZD'
        user1_fb_user_id = '110000369505832'
        user2_fb_auth_token = 'EAACEFGIZCorABANb4jkcIiUKSLfXGKU15TRrQ6yRyTXZBT4MeD2l0M3eMJ6E86aoJ1149vL5E7ZAtVAisipCOQH7E5UN9XuAhSIaWnpZCJe9ZApmC0AZBFXkZA6ZC1U7uI8j9WpfCGs0qnmFUkbYKy1vDO83jiAIZCWwuqn5CUwc3tOAG2xKucDN3'
        user2_fb_user_id = '131453847271362'

        user1_response = self.c.post('/users/', json.dumps({'fb_auth_token': user1_fb_auth_token, 'fb_user_id': user1_fb_user_id}), content_type="application/json")
        user2_response = self.c.post('/users/', json.dumps({'fb_auth_token': user2_fb_auth_token, 'fb_user_id': user2_fb_user_id}), content_type="application/json")

        self.user1_json = json.loads(user1_response.content)
        self.user2_json = json.loads(user2_response.content)

    def test_no_messages(self):
        query_string = '/users/'+self.user1_json['fb_user_id']+\
                       '/messages?real_auth_token='+self.user1_json['real_auth_token']+\
                       '&match_user='+self.user2_json['fb_user_id']
        response = self.c.get(query_string)
        self.assertEqual(json.loads(json.loads(response.content)), [])

    def test_send_one_message(self):
        # Send the message
        query_string = '/users/' + self.user1_json['fb_user_id'] + '/messages/'
        query_params = {
            'real_auth_token': self.user1_json['real_auth_token'],
            'match_user': self.user2_json['fb_user_id'],
            'message_content': 'This is the first message'
        }
        self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/'+self.user1_json['fb_user_id'] +\
                       '/messages?real_auth_token='+self.user1_json['real_auth_token']+\
                       '&match_user='+self.user2_json['fb_user_id']
        response = self.c.get(query_string)

        self.assertEqual(json.loads(json.loads(response.content))[0]['message_content'], 'This is the first message')
        self.assertEqual(json.loads(json.loads(response.content))[0]['message_index'], 0)
        self.assertEqual(json.loads(json.loads(response.content))[0]['sent_by_match'], False)

        # Test GET response for user who received the message
        query_string = '/users/' + self.user2_json['fb_user_id'] +\
                       '/messages?real_auth_token=' + self.user2_json['real_auth_token'] + \
                       '&match_user=' + self.user1_json['fb_user_id']
        response = self.c.get(query_string)

        self.assertEqual(json.loads(json.loads(response.content))[0]['message_content'], 'This is the first message')
        self.assertEqual(json.loads(json.loads(response.content))[0]['message_index'], 0)
        self.assertEqual(json.loads(json.loads(response.content))[0]['sent_by_match'], True)

    def test_send_twenty_messages(self):
        # Send the messages
        for i in range(0,20):
            query_string = '/users/' + self.user1_json['fb_user_id'] + '/messages/'
            query_params = {
                'real_auth_token': self.user1_json['real_auth_token'],
                'match_user': self.user2_json['fb_user_id'],
                'message_content': i
            }
            self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/' + self.user1_json['fb_user_id'] +\
                       '/messages?real_auth_token=' + self.user1_json['real_auth_token'] + \
                       '&match_user=' + self.user2_json['fb_user_id']
        response = self.c.get(query_string)
        self.assertEqual(len(json.loads(json.loads(response.content))), 20)

    def test_send_forty_messages(self):
        # Send the messages
        for i in range(0, 40):
            query_string = '/users/' + self.user1_json['fb_user_id'] + '/messages/'
            query_params = {
                'real_auth_token': self.user1_json['real_auth_token'],
                'match_user': self.user2_json['fb_user_id'],
                'message_content': i
            }
            self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/' + self.user1_json['fb_user_id'] +\
                       '/messages?real_auth_token=' + self.user1_json['real_auth_token'] + \
                       '&match_user=' + self.user2_json['fb_user_id']
        response = self.c.get(query_string)
        self.assertEqual(len(json.loads(json.loads(response.content))), 20)
        self.assertEqual(json.loads(json.loads(response.content))[19]['message_index'], 20)

        # Test GET response for last seen index
        query_string = '/users/' + self.user1_json['fb_user_id'] +\
                       '/messages?real_auth_token=' + self.user1_json['real_auth_token'] + \
                       '&match_user=' + self.user2_json['fb_user_id'] +\
                       '&message_index=20'
        response = self.c.get(query_string)
        self.assertEqual(len(json.loads(json.loads(response.content))), 20)
        self.assertEqual(json.loads(json.loads(response.content))[19]['message_index'], 0)

    def test_back_and_forth_messages(self):
        #User 1 sends a message
        query_string = '/users/' + self.user1_json['fb_user_id'] + '/messages/'
        query_params = {
            'real_auth_token': self.user1_json['real_auth_token'],
            'match_user': self.user2_json['fb_user_id'],
            'message_content': 'This is the first message'
        }
        self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/'+self.user1_json['fb_user_id'] +\
                       '/messages?real_auth_token='+self.user1_json['real_auth_token']+\
                       '&match_user='+self.user2_json['fb_user_id']
        response = self.c.get(query_string)

        self.assertEqual(json.loads(json.loads(response.content))[0]['message_content'], 'This is the first message')
        self.assertEqual(json.loads(json.loads(response.content))[0]['message_index'], 0)
        self.assertEqual(json.loads(json.loads(response.content))[0]['sent_by_match'], False)

        # Test GET response for user who received the message
        query_string = '/users/' + self.user2_json['fb_user_id'] +\
                       '/messages?real_auth_token=' + self.user2_json['real_auth_token'] + \
                       '&match_user=' + self.user1_json['fb_user_id']
        response = self.c.get(query_string)

        self.assertEqual(json.loads(json.loads(response.content))[0]['message_content'], 'This is the first message')
        self.assertEqual(json.loads(json.loads(response.content))[0]['message_index'], 0)
        self.assertEqual(json.loads(json.loads(response.content))[0]['sent_by_match'], True)

        #User 2 sends a message
        query_string = '/users/' + self.user2_json['fb_user_id'] + '/messages/'
        query_params = {
            'real_auth_token': self.user2_json['real_auth_token'],
            'match_user': self.user1_json['fb_user_id'],
            'message_content': 'That was a boring first message'
        }
        self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/'+self.user2_json['fb_user_id'] +\
                       '/messages?real_auth_token='+self.user2_json['real_auth_token']+\
                       '&match_user='+self.user1_json['fb_user_id']
        response = self.c.get(query_string)

        self.assertEqual(json.loads(json.loads(response.content))[0]['message_content'], 'That was a boring first message')
        self.assertEqual(json.loads(json.loads(response.content))[0]['message_index'], 1)
        self.assertEqual(json.loads(json.loads(response.content))[0]['sent_by_match'], False)

        # Test GET response for user who received the message
        query_string = '/users/' + self.user1_json['fb_user_id'] +\
                       '/messages?real_auth_token=' + self.user1_json['real_auth_token'] + \
                       '&match_user=' + self.user2_json['fb_user_id']
        response = self.c.get(query_string)

        self.assertEqual(json.loads(json.loads(response.content))[0]['message_content'], 'That was a boring first message')
        self.assertEqual(json.loads(json.loads(response.content))[0]['message_index'], 1)
        self.assertEqual(json.loads(json.loads(response.content))[0]['sent_by_match'], True)