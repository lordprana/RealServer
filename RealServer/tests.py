from cStringIO import StringIO
from datetime import datetime

from PIL import Image
from django.test import TestCase

from RealServer import facebook
from api.models import User
from tools import nextDayOfWeekToDatetime, cropImageToSquare, cropImageByAspectRatio, cropImageByAspectRatioAndCoordinates, cropImage


class FacebookTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(fb_user_id='122700428234141', most_recent_fb_auth_token='EAACEFGIZCorABABwneNGNfqZAmeQI2QlftiHN7gkf2Ok4kJaZCbOo10XbD3wZAeaOFzYVaZBYOPoLPoF3VpygpZAZAOmOJbRgfp09h7Wp1g5vIpsZAuVpqVu3k8lYXkt6GJgCPsH43hecd7o8TueBOxt9lZAgWcyoCRuBjhLZBl5WBFvMW3RhQS5VohkYzTJgpQDGDHMM8t3oNjAZDZD')
        self.user2 = User.objects.create(fb_user_id='116474138858424', most_recent_fb_auth_token='EAACEFGIZCorABADEzDQtokRhCZCv7jFt6mXCvZCXxwNiNL58sM9rHD6raZCcSTQfDkkEEr2X7MbwxrwLMU6ypLg3Or8XyfG1ezAvZCYpGL4CubswaZCn7ZBvEePLCcDhZBYe3Gzq6qhqEPKQNLvRKB43VtwC5jrpG4KzDz2i9seXfrMZBhCsoHf40dhPl9M3r54tAxxP64Ge90wZDZD')
        self.user3 = User.objects.create(fb_user_id='2959531196950', most_recent_fb_auth_token='EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum')
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
        user_picture = facebook.getUserProfilePicture(self.user3)
        self.assertEqual(user_picture[:11], '\xff\xd8\xff\xe0\x00\x10JFIF\x00') # This string begins every picture returned by Facebook

        # Test returns none if bad request
        self.user3.most_recent_fb_auth_token = 'EAACE'
        self.user3.save()
        user_picture = facebook.getUserProfilePicture(self.user1)
        self.assertEqual(user_picture, None)

class ToolsTest(TestCase):
    def setUp(self):
        self.user2 = User.objects.create(fb_user_id='122700428234141',most_recent_fb_auth_token='EAACEFGIZCorABAJ6TTrnVfxoyP2xs5jqQYgemBaqZBgQhV1ZC2VkFwzdarZAuTsRI6HJte7olP712H2FV73UbprxHA94Dq8twNLKZCPwZB57ZBhheXWFBPH5XWCtVk9sAmr65ZCKVneFufSplL0DbqoRnvTLdBkaS86KrWCNxypQtq9ZBxSBW9ym8zmaBoKsBPskZD')
        self.user3 = User.objects.create(fb_user_id='2959531196950', most_recent_fb_auth_token='EAACEFGIZCorABAELkmH1UiKQaJi8IJYA8oPBUHcJ7MggYxZBoYI8XOOUlh9IIhTamaDIyYrPSQmkYM4ChfPI8u2OT7LjJYTseQFF4O9J7xH40iQZAjAXGCgzi27pkM468GUOV6mJwKE3qLqdpum')
    def test_day_of_week_difference(self):
        dt = datetime(year=2017, month=1, day=16)
        dt = nextDayOfWeekToDatetime(dt, 'wed')
        self.assertEqual(dt, datetime(year=2017, month=1, day=18))
        dt = datetime(year=2017, month=1, day=16)
        dt = nextDayOfWeekToDatetime(dt, 'sun')
        self.assertEqual(dt, datetime(year=2017, month=1, day=22))
        dt = nextDayOfWeekToDatetime(dt, 'tue')
        self.assertEqual(dt, datetime(year=2017, month=1, day=24))
        dt = datetime(year=2017, month=1, day=19)
        dt = nextDayOfWeekToDatetime(dt, 'thur')
        self.assertEqual(dt, datetime(year=2017, month=1, day=19))

    def test_crop_image_to_square(self):
        # Test Portrait Orientation
        user_picture = facebook.getUserProfilePicture(self.user3)
        file_jpgdata = StringIO(user_picture)
        image = Image.open(file_jpgdata)
        w, h = image.size
        self.assertNotEqual(w, h)
        image = cropImageToSquare(image)
        self.assertEqual(image.size[0], image.size[1])

        # Test Landscape Orientation
        image = Image.open('RealServer/mediafiles/2959531196950/landscape_test.jpg')
        w, h = image.size
        self.assertNotEqual(w, h)
        image = cropImageToSquare(image)
        self.assertEqual(image.size[0], image.size[1])

    def test_crop_image_by_aspect_ratio(self):
        # Test Portrait Orientation
        user_picture = facebook.getUserProfilePicture(self.user3)
        file_jpgdata = StringIO(user_picture)
        image = Image.open(file_jpgdata)
        w, h = image.size
        aspect_width = 205.0
        aspect_height = 365.0
        self.assertNotEqual(aspect_width/aspect_height, float(w)/float(h))
        image = cropImageByAspectRatio(image, aspect_width, aspect_height)
        w, h = image.size
        self.assertEqual(round(aspect_width/aspect_height, 2), round(float(w)/float(h), 2))

    def test_crop_image(self):
        user_picture = facebook.getUserProfilePicture(self.user3)
        file_jpgdata = StringIO(user_picture)
        image = Image.open(file_jpgdata)
        w, h = image.size
        start_cropx = 460
        start_cropy = 87
        end_cropx = 889
        end_cropy = 513
        image = cropImage(image, start_cropx, start_cropy, end_cropx, end_cropy)
        w, h = image.size
        self.assertEqual(w, end_cropx - start_cropx)
        self.assertEqual(h, end_cropy- start_cropy)

    def test_crop_image_by_aspect_ratio_and_coordinates(self):
        # Test with facebook photo (landscape orientation)
        user_picture = facebook.getUserProfilePicture(self.user3)
        file_jpgdata = StringIO(user_picture)
        image = Image.open(file_jpgdata)
        w, h = image.size
        aspect_width = 205.0
        aspect_height = 365.0
        self.assertNotEqual(aspect_width / aspect_height, float(w) / float(h))
        image = cropImageByAspectRatioAndCoordinates(image, 460, 87, 889, 513, aspect_width, aspect_height)
        w, h = image.size
        self.assertEqual(round(aspect_width/aspect_height, 2), round(float(w)/float(h), 2))
        image.close()

        # Test with another photo (portrait orientation)
        image = Image.open('RealServer/mediafiles/2959531196950/obama_test.jpg')
        w, h = image.size
        aspect_width = 205.0
        aspect_height = 365.0
        self.assertNotEqual(aspect_width / aspect_height, float(w) / float(h))
        image = cropImageByAspectRatioAndCoordinates(image, 63, 137, 1260, 1331, aspect_width, aspect_height)
        w, h = image.size
        self.assertEqual(round(aspect_width / aspect_height, 2), round(float(w) / float(h), 2))

        # Test with another photo (landscape orientation)
        image = Image.open('RealServer/mediafiles/2959531196950/landscape_test.jpg')
        w, h = image.size
        aspect_width = 205.0
        aspect_height = 365.0
        self.assertNotEqual(aspect_width / aspect_height, float(w) / float(h))
        image = cropImageByAspectRatioAndCoordinates(image, 1338, 253, 1690, 629, aspect_width, aspect_height)
        w, h = image.size
        self.assertEqual(round(aspect_width / aspect_height, 2), round(float(w) / float(h), 2))

        # Test with another photo (square orientation)
        image = Image.open('RealServer/mediafiles/2959531196950/square_test.png')
        w, h = image.size
        aspect_width = 205.0
        aspect_height = 365.0
        self.assertNotEqual(aspect_width / aspect_height, float(w) / float(h))
        image = cropImageByAspectRatioAndCoordinates(image, 1, 1, 300, 300, aspect_width, aspect_height)
        w, h = image.size
        self.assertEqual(round(aspect_width / aspect_height, 2), round(float(w) / float(h), 2))