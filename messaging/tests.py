from django.test import TestCase
from django.test import Client
from api.models import User
from model_mommy import mommy
from rest_framework.authtoken.models import Token
from messaging.models import Message
import json

# Create your tests here.

class MessagingTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        # Create test users using users endpoint
        user1_fb_auth_token = 'EAACEFGIZCorABAAVi37QvXCIxVvZAlbG0NKWOiAWRdko6kZB6WH9Mrdh82AL8pUE1FCPUOIZA81H5hZAfZAC1QSf8iTL56jE3WWZCrOXvQFF4OPjdo0WZAn23aEbjyG2GIJ385nTBUwOhj4bU6LF9fLhTyrjXY2LUeuSPmr2IifI6M32HBknHlQdpZCHsPFOc5ZBCxvuNJ9ohtGUZBFljS9GXHU'
        user1_fb_user_id = '110000369505832'
        user2_fb_auth_token = 'EAACEFGIZCorABALHO1tYw4FrFh7WqZAgCInp0jekXF8Dfum1PreZBhQ2ZBNwmYaZCBH9RJdE0ZA3vY8uEHEZAmtUAos4h6OmUtR8FDpwHzYUs42dna6NyRqp0PWZAEQSuaZBdBbgJPlPpCLVwUSMQ5WxN6ngxOoaI0zB3ie5h2q1SqoqiZCZC8ny8rb0ALLdW2avSrsBTzZBCRWoflB80oyRZAIQ1'
        user2_fb_user_id = '131453847271362'

        self.user1 = User.objects.create(fb_user_id=user1_fb_user_id, most_recent_fb_auth_token=user1_fb_auth_token)
        self.user2 = User.objects.create(fb_user_id=user2_fb_user_id, most_recent_fb_auth_token=user2_fb_auth_token)
        self.real_auth_token1 = Token.objects.create(user=self.user1)
        self.real_auth_token2 = Token.objects.create(user=self.user2)
        self.user1.real_auth_token = self.real_auth_token1.key
        self.user2.real_auth_token = self.real_auth_token2.key
        self.user1.save()
        self.user2.save()

        #user1_response = self.c.post('/users/', json.dumps({'fb_auth_token': user1_fb_auth_token, 'fb_user_id': user1_fb_user_id}), content_type="application/json")
        #user2_response = self.c.post('/users/', json.dumps({'fb_auth_token': user2_fb_auth_token, 'fb_user_id': user2_fb_user_id}), content_type="application/json")

        #self.user1_json = json.loads(user1_response.content)
        #self.user2_json = json.loads(user2_response.content)

    def test_no_messages(self):
        query_string = '/users/'+self.user1.fb_user_id+\
                       '/messages?real_auth_token='+self.user1.real_auth_token+\
                       '&match_user='+self.user2.fb_user_id
        response = self.c.get(query_string)
        self.assertEqual(json.loads(response.content), [])

    def test_send_one_message(self):
        date = mommy.make('matchmaking.date')
        # Send the message
        query_string = '/users/' + self.user1.fb_user_id + '/messages/'
        query_params = {
            'real_auth_token': self.user1.real_auth_token,
            'match_user': self.user2.fb_user_id,
            'message_content': 'This is the first message',
            'date_id': date.pk
        }
        self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/'+self.user1.fb_user_id +\
                       '/messages?real_auth_token='+self.user1.real_auth_token+\
                       '&match_user='+self.user2.fb_user_id
        response = self.c.get(query_string)
        json_response = json.loads(response.content)

        self.assertEqual(json_response[0]['message_content'], 'This is the first message')
        self.assertEqual(json_response[0]['message_index'], 0)
        self.assertEqual(json_response[0]['sent_by_match'], False)

        # Test GET response for user who received the message
        query_string = '/users/' + self.user2.fb_user_id +\
                       '/messages?real_auth_token=' + self.user2.real_auth_token + \
                       '&match_user=' + self.user1.fb_user_id
        response = self.c.get(query_string)
        json_response = json.loads(response.content)

        self.assertEqual(json_response[0]['message_content'], 'This is the first message')
        self.assertEqual(json_response[0]['message_index'], 0)
        self.assertEqual(json_response[0]['sent_by_match'], True)

    def test_send_twenty_messages(self):
        date = mommy.make('matchmaking.date')
        # Send the messages
        for i in range(0,20):
            query_string = '/users/' + self.user1.fb_user_id + '/messages/'
            query_params = {
                'real_auth_token': self.user1.real_auth_token,
                'match_user': self.user2.fb_user_id,
                'message_content': i,
                'date_id': date.pk
            }
            self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/' + self.user1.fb_user_id +\
                       '/messages?real_auth_token=' + self.user1.real_auth_token + \
                       '&match_user=' + self.user2.fb_user_id
        response = self.c.get(query_string)
        self.assertEqual(len(json.loads(response.content)), 20)

    def test_send_forty_messages(self):
        date = mommy.make('matchmaking.date')
        # Send the messages
        for i in range(0, 40):
            query_string = '/users/' + self.user1.fb_user_id + '/messages/'
            query_params = {
                'real_auth_token': self.user1.real_auth_token,
                'match_user': self.user2.fb_user_id,
                'message_content': i,
                'date_id': date.pk
            }
            self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/' + self.user1.fb_user_id +\
                       '/messages?real_auth_token=' + self.user1.real_auth_token + \
                       '&match_user=' + self.user2.fb_user_id
        response = self.c.get(query_string)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json), 20)
        self.assertEqual(response_json[19]['message_index'], 20)
        self.assertEqual(response_json[0]['message_index'], 39)

        # Test GET response for last seen index
        query_string = '/users/' + self.user1.fb_user_id +\
                       '/messages?real_auth_token=' + self.user1.real_auth_token + \
                       '&match_user=' + self.user2.fb_user_id +\
                       '&message_index=20'
        response = self.c.get(query_string)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json), 20)
        self.assertEqual(response_json[19]['message_index'], 0)
        self.assertEqual(response_json[0]['message_index'], 19)

    def test_back_and_forth_messages(self):
        date = mommy.make('matchmaking.date')
        #User 1 sends a message
        query_string = '/users/' + self.user1.fb_user_id + '/messages/'
        query_params = {
            'real_auth_token': self.user1.real_auth_token,
            'match_user': self.user2.fb_user_id,
            'message_content': 'This is the first message',
            'date_id': date.pk
        }
        self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/'+self.user1.fb_user_id +\
                       '/messages?real_auth_token='+self.user1.real_auth_token+\
                       '&match_user='+self.user2.fb_user_id
        response = self.c.get(query_string)
        response_json = json.loads(response.content)
        message = Message.objects.get(pk=response_json[0]['message_id'])

        self.assertEqual(response_json[0]['message_content'], 'This is the first message')
        self.assertEqual(response_json[0]['message_index'], 0)
        self.assertEqual(response_json[0]['sent_by_match'], False)
        self.assertEqual(message.read, False)

        # Test GET response for user who received the message
        query_string = '/users/' + self.user2.fb_user_id +\
                       '/messages?real_auth_token=' + self.user2.real_auth_token + \
                       '&match_user=' + self.user1.fb_user_id
        response = self.c.get(query_string)
        response_json = json.loads(response.content)
        message = Message.objects.get(pk=response_json[0]['message_id'])

        self.assertEqual(response_json[0]['message_content'], 'This is the first message')
        self.assertEqual(response_json[0]['message_index'], 0)
        self.assertEqual(response_json[0]['sent_by_match'], True)
        self.assertEqual(message.read, True)

        #User 2 sends a message
        query_string = '/users/' + self.user2.fb_user_id + '/messages/'
        query_params = {
            'real_auth_token': self.user2.real_auth_token,
            'match_user': self.user1.fb_user_id,
            'message_content': 'That was a boring first message',
            'date_id': date.pk
        }
        self.c.post(query_string, json.dumps(query_params), content_type="application/json")

        # Test GET response for user who sent message
        query_string = '/users/'+self.user2.fb_user_id +\
                       '/messages?real_auth_token='+self.user2.real_auth_token+\
                       '&match_user='+self.user1.fb_user_id
        response = self.c.get(query_string)
        response_json = json.loads(response.content)
        message = Message.objects.get(pk=response_json[0]['message_id'])

        self.assertEqual(response_json[0]['message_content'], 'That was a boring first message')
        self.assertEqual(response_json[0]['message_index'], 1)
        self.assertEqual(response_json[0]['sent_by_match'], False)
        self.assertEqual(message.read, False)

        # Test GET response for user who received the message
        query_string = '/users/' + self.user1.fb_user_id +\
                       '/messages?real_auth_token=' + self.user1.real_auth_token + \
                       '&match_user=' + self.user2.fb_user_id
        response = self.c.get(query_string)
        response_json = json.loads(response.content)
        message = Message.objects.get(pk=response_json[0]['message_id'])

        self.assertEqual(response_json[0]['message_content'], 'That was a boring first message')
        self.assertEqual(response_json[0]['message_index'], 1)
        self.assertEqual(response_json[0]['sent_by_match'], True)
        self.assertEqual(message.read, True)