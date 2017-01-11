from django.test import TestCase
import facebook
from api.models import User

class FacebookTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(fb_user_id='122700428234141', most_recent_fb_auth_token='EAACEFGIZCorABABzwJMoPKu9Tnk72G5QaZCaT29jesBZA919nNYpEcbwee9inG6d1LKwMiq6fJkf3icW1Suiye0qPTwtPt6klWv5ZA4ZAkv4vXVZBjcJpN3xBlTQI80z9jJbvSEfQY5kX2vDpTjwSBoAik4BZCptGsFqtrR0yeL9lKxmZCam1rqCVlZA4wSOC9nMUybIaBOnLpgZDZD')
        self.user2 = User.objects.create(fb_user_id='116474138858424', most_recent_fb_auth_token='EAACEFGIZCorABADEzDQtokRhCZCv7jFt6mXCvZCXxwNiNL58sM9rHD6raZCcSTQfDkkEEr2X7MbwxrwLMU6ypLg3Or8XyfG1ezAvZCYpGL4CubswaZCn7ZBvEePLCcDhZBYe3Gzq6qhqEPKQNLvRKB43VtwC5jrpG4KzDz2i9seXfrMZBhCsoHf40dhPl9M3r54tAxxP64Ge90wZDZD')

    def test_mutual_friends(self):
        mutual_friends_json = facebook.getMutualFriends(self.user1, self.user2)
        self.assertEqual(mutual_friends_json['summary']['total_count'], 2)
        self.assertEqual(mutual_friends_json['data'][0]['name'], 'Barbara McDonaldman')