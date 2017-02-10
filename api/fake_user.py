from api.models import User, Gender, SexualPreference, Status
from RealServer.tools import cropImageToSquare, cropImageByAspectRatio
from RealServer.aws import s3_generate_presigned_post
from datetime import time
from PIL import Image
from StringIO import StringIO
import random
import json
import requests
import os
import string

female_names = [
    'Sophia',
    'Emma',
    'Olivia',
    'Ava',
    'Isabella',
    'Mia',
    'Zoe',
    'Lily',
    'Emily',
    'Madelyn'
]

male_names = [
    'Jackson',
    'Aiden',
    'Liam',
    'Lucas',
    'Noah',
    'Mason',
    'Ethan',
    'Caden',
    'Jacob',
    'Logan'
]

occupations = [
    'Accountant',
    'Nurse',
    'Teacher',
    'Software Engineer',
    'Doctor',
    'Salesperson',
    'Chef',
    'Veterinarian',
    'Dog Walker',
    'Lawyer',
    'Social Worker',
    'Bartender',
    'General Manager',
    'Administrative Assistant'
]

schools = [
    'Monmouth College',
    'Baylor University',
    'Texas Tech University',
    'The University of Texas at Austin',
    'Angelo State University',
    'LSU',
    'University of North Texas',
    'Tulane University',
    'New Mexico State University',
    'The University of Oklahoma'
]

def generate_random_fake_fb_user_id():
    return ''.join(random.choice(string.lowercase) for i in range(299)) # 299 is less than the max_length of the fb_user_id charfield

# Creates a fake user and saves to database
def generate_fake_user(gender, latitude, longitude):
    fake_user = User.objects.create(fb_user_id=generate_random_fake_fb_user_id(), most_recent_fb_auth_token='fake')
    if gender == Gender.MAN.value:
        fake_user.first_name = random.choice(male_names)
        fake_user.gender = Gender.MAN.value
        pic_number = str(random.randint(4,6))
        picture1_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/1_portrait'
        picture1_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/1_square'
        picture2_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/2_portrait'
        picture2_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/2_square'
        picture3_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/3_portrait'
        picture3_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/3_square'
    elif gender == Gender.WOMAN.value:
        fake_user.first_name = random.choice(female_names)
        fake_user.gender = Gender. WOMAN.value
        pic_number = str(random.randint(1, 3))
        picture1_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/1_portrait'
        picture1_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/1_square'
        picture2_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/2_portrait'
        picture2_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/2_square'
        picture3_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/3_portrait'
        picture3_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + pic_number + '/3_square'
    fake_user.age = random.randint(18,35)
    fake_user.interested_in = SexualPreference.BISEXUAL.value
    fake_user.occupation = random.choice(occupations)
    fake_user.education = random.choice(schools)
    fake_user.about = 'I love pizza and dogs.'
    fake_user.status = Status.FINISHED_PROFILE.value
    fake_user.latitude = latitude
    fake_user.longitude = longitude

    fake_user.likes_drinks = True
    fake_user.likes_food = True
    fake_user.likes_coffee = True
    fake_user.likes_parks = True
    fake_user.likes_museums = True
    fake_user.likes_fun = True

    fake_user.sun_start_time = time(hour=8)
    fake_user.sun_end_time = time(hour=23, minute=59, second=59)
    fake_user.mon_start_time = time(hour=8)
    fake_user.mon_end_time = time(hour=23, minute=59, second=59)
    fake_user.tue_start_time = time(hour=8)
    fake_user.tue_end_time = time(hour=23, minute=59, second=59)
    fake_user.wed_start_time = time(hour=8)
    fake_user.wed_end_time = time(hour=23, minute=59, second=59)
    fake_user.thur_start_time = time(hour=8)
    fake_user.thur_end_time = time(hour=23, minute=59, second=59)
    fake_user.fri_start_time = time(hour=8)
    fake_user.fri_end_time = time(hour=23, minute=59, second=59)
    fake_user.sat_start_time = time(hour=8)
    fake_user.sat_end_time = time(hour=23, minute=59, second=59)

    fake_user.save()

def crop_fake_user_picture_and_upload_to_s3(file_path, user_num, pic_num):
    os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAI4755USWAQYAFTUA'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'xBjhBPWks/IxGm89l1oHQ9GE0ZE27jRTreX5yIon'
    os.environ['S3_BUCKET'] = 'realdatingbucket'

    image = Image.open(file_path)
    square_user_picture = cropImageToSquare(image)
    s3_file_path = 'fake_user/' + user_num + '/' + pic_num + '_square'
    request_json = json.loads(s3_generate_presigned_post('.jpg', None, s3_file_path))
    # Save Pillow image to StringIO to send in post request
    img_io = StringIO()
    square_user_picture.save(img_io, 'JPEG', quality=100)
    img_io.seek(0)
    files = {'file': img_io.read()}
    r = requests.post(request_json['data']['url'], data=request_json['data']['fields'], files=files)

    aspect_width = 205
    aspect_height = 365
    image = Image.open(file_path)
    portrait_user_picture = cropImageByAspectRatio(image, aspect_width, aspect_height)
    s3_file_path = 'fake_user/' + user_num + '/' + pic_num + '_portrait'
    request_json = json.loads(s3_generate_presigned_post('.jpg', None, s3_file_path))
    # Save Pillow image to StringIO to send in post request
    img_io = StringIO()
    portrait_user_picture.save(img_io, 'JPEG', quality=100)
    img_io.seek(0)
    files = {'file': img_io.read()}
    r = requests.post(request_json['data']['url'], data=request_json['data']['fields'], files=files)