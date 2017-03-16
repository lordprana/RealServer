from api.models import User, Gender, SexualPreference, Status
from RealServer.tools import cropImageToSquare, cropImageByAspectRatio
from RealServer.aws import s3_generate_presigned_post
from datetime import time
from loremipsum import get_sentences
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
    'Madelyn',
    'Harper',
    'Madison',
    'Elizabeth',
    'Evelyn',
    'Avery',
    'Chloe',
    'Ella',
    'Grace',
    'Victoria',
    'Aubrey',
    'Scarlett',
    'Addison',
    'Lillian',
    'Natalie',
    'Hannah',
    'Aria',
    'Layla',
    'Brooklyn',
    'Alexa',
    'Penelope',
    'Riley',
    'Leah',
    'Audrey',
    'Savannah',
    'Allison',
    'Samantha',
    'Nora',
    'Skylar',
    'Camila',
    'Anna',
    'Paisley',
    'Ariana',
    'Ellie',
    'Aaliyah',
    'Claire',
    'Violet',
    'Stella',
    'Sadie',
    'Mila',
    'Gabriella',
    'Lucy',
    'Arianna',
    'Kennedy',
    'Sarah',
    'Madelyn',
    'Eleanor',
    'Kaylee',
    'Caroline',
    'Hazel',
    'Hailey',
    'Genesis',
    'Kylie',
    'Autumn',
    'Piper',
    'Maya',
    'Neveah',
    'Serenity',
    'Peyton',
    'Mackenzie',
    'Bella',
    'Eva',
    'Taylor',
    'Naomi',
    'Aubree',
    'Aurora',
    'Melanie',
    'Lydia',
    'Brianna',
    'Ruby',
    'Katherine',
    'Ashley',
    'Alexis',
    'Alice',
    'Cora',
    'Julia',
    'Madeline',
    'Faith',
    'Anabelle',
    'Alyssa',
    'Isabelle',
    'Vivian',
    'Gianna',
    'Quinn',
    'Clara',
    'Reagan',
    'Khloe'
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
    'Logan',
    'William',
    'James',
    'Alexander',
    'Michael',
    'Benjamin',
    'Elijah',
    'Daniel',
    'Logan',
    'Matthew',
    'David',
    'Oliver',
    'Jayden',
    'Joseph',
    'Gabriel',
    'Samuel',
    'Carter',
    'Anthony',
    'John',
    'Dylan',
    'Luke',
    'Henry',
    'Andrew',
    'Isaac',
    'Christopher',
    'Joshua',
    'Wyatt',
    'Sebastian',
    'Owen',
    'Caleb',
    'Nathan',
    'Ryan',
    'Jack',
    'Hunter',
    'Levi',
    'Christian',
    'Jaxon',
    'Julian',
    'Landon',
    'Grayson',
    'Jonathan',
    'Isaiah',
    'Charles',
    'Thomas',
    'Aaron',
    'Eli',
    'Connor',
    'Jeremiah',
    'Cameron',
    'Josian',
    'Adrian',
    'Colton',
    'Jordan',
    'Brayden',
    'Nicholas',
    'Robert',
    'Angel',
    'Hudson',
    'Lincoln',
    'Evan',
    'Dominic',
    'Austin',
    'Gavin',
    'Nolan',
    'Parker',
    'Adam',
    'Chase',
    'Jace',
    'Ian',
    'Cooper',
    'Easton',
    'Kevin',
    'Jose',
    'Tyler',
    'Brandon',
    'Asher',
    'Jaxson',
    'Mateo',
    'Jason',
    'Ayden',
    'Zachary',
    'Carson',
    'Xavier',
    'Leo',
    'Ezra',
    'Bentley',
    'Sawyer',
    'Kayden',
    'Blake',
    'Nathaniel',
    'Ryder',
    'Theodore',
    'Elias'
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
    'Administrative Assistant',
    'Retail',
    'Cashier',
    'Office clerk',
    'Accountant',
    'Nanny',
    'Carpenter',
    'Childcare worker',
    'Management Analyst',
    'Medical Assistant',
    'Electrician',
    'Financial Manager',
    'HR Specialist',
    'Hairstylist',
    'Pharmacy Technician',
    'Pharmacist',
    'Firefighter',
    'Dental Assistant',
    'Social Worker',
    'Claims Adjuster',
    'Civil Engineer',
    'Paralegal',
    'School Counselor',
    'Mechanical Engineer',
    'Insurance Clerk',
    'PR Specialist',
    'Personal Trainer',
    'EMT',
    'Industrial Engineer',
    'Graphic Designer',
    'Painter',
    'Food Service Manager',
    'Physical Therapist',
    'Dentist',
    'Marketing Manager',
    'Real Estate Agent',
    'Electrical Engineer',
    'Librarian',
    'Baker',
    'Flight Attendant'
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
    'The University of Oklahoma',
    'Stephen F. Austin State University',
    'DuVall\'s School of Cosmetology',
    'UMKC',
    'Lindenwood University-Belleville Campus',
    'Mizzou',
    'Texas A&M University',
    'University of Texas at Tyler',
    'Oklahoma Christian University',
    'University of Mississippi',
    'Virginia Tech',
    'Northeastern University',
    'North Central Texas College',
    'The University of Alabama',
    'Texas State University',
    'Oklahoma State University',
    'Parker University',
    'University of Arkansas'

]

def generate_random_fake_fb_user_id():
    return ''.join(random.choice(string.lowercase) for i in range(299)) # 299 is less than the max_length of the fb_user_id charfield

# Creates a fake user and saves to database
def generate_fake_user(gender, latitude, longitude):
    fake_user = User.objects.create(fb_user_id=generate_random_fake_fb_user_id(), most_recent_fb_auth_token='fake')
    fake_user.is_fake_user = True
    if gender == Gender.MAN.value:
        fake_user.first_name = random.choice(male_names)
        fake_user.gender = Gender.MAN.value
        pic_number = str(random.randint(1,21))
        fake_user.picture1_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/1_portrait'
        fake_user.picture1_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/1_square'
        fake_user.picture2_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/2_portrait'
        fake_user.picture2_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/2_square'
        fake_user.picture3_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/3_portrait'
        fake_user.picture3_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/3_square'
    elif gender == Gender.WOMAN.value:
        fake_user.first_name = random.choice(female_names)
        fake_user.gender = Gender. WOMAN.value
        pic_number = str(random.randint(1, 21))
        fake_user.picture1_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/1_portrait'
        fake_user.picture1_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/1_square'
        fake_user.picture2_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/2_portrait'
        fake_user.picture2_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/2_square'
        fake_user.picture3_portrait_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/3_portrait'
        fake_user.picture3_square_url = 'http://realdatingbucket.s3.amazonaws.com/fake_user/' + gender + '/' + pic_number + '/3_square'
    fake_user.age = random.randint(18,35)
    fake_user.interested_in = SexualPreference.BISEXUAL.value
    fake_user.occupation = random.choice(occupations)
    fake_user.education = random.choice(schools)
    about_length = random.randint(0,5)
    if about_length:
        fake_user.about = ' '.join(get_sentences(about_length))
    else:
        fake_user.about = ''
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
    return fake_user

def crop_fake_user_picture_and_upload_to_s3(file_path, user_num, pic_num, gender):
    os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAI4755USWAQYAFTUA'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'xBjhBPWks/IxGm89l1oHQ9GE0ZE27jRTreX5yIon'
    os.environ['S3_BUCKET'] = 'realdatingbucket'

    image = Image.open(file_path)
    square_user_picture = cropImageToSquare(image)
    s3_file_path = 'fake_user/' + gender + '/' + user_num + '/' + pic_num + '_square'
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
    s3_file_path = 'fake_user/' + gender + '/' + user_num + '/' + pic_num + '_portrait'
    request_json = json.loads(s3_generate_presigned_post('.jpg', None, s3_file_path))
    # Save Pillow image to StringIO to send in post request
    img_io = StringIO()
    portrait_user_picture.save(img_io, 'JPEG', quality=100)
    img_io.seek(0)
    files = {'file': img_io.read()}
    r = requests.post(request_json['data']['url'], data=request_json['data']['fields'], files=files)