from django.test import TestCase
from api.auth import AuthenticationBackend
from api.models import User
from rest_framework.authtoken.models import Token

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