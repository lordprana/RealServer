"""
Django settings for RealServer project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from decouple import config
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

#SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
#DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    SECRET_KEY = 'a6k!h$u$49@o#at@7-!=5^_)(a7c13$48n@@r2v-ge4ae9e3v7'
else:
    SECRET_KEY = os.environ['SECRET_KEY']


ALLOWED_HOSTS = ['*']

AWS_ACCESS_KEY_ID = 'AKIAI4755USWAQYAFTUA'
AWS_SECRET_ACCESS_KEY = 'xBjhBPWks/IxGm89l1oHQ9GE0ZE27jRTreX5yIon'
S3_BUCKET = 'realdatingbucket'

FAKE_USERS = True

# Application definition

FB_APP_ID = '145223082549936'
FB_APP_SECRET = 'e03cc02eb74e7a8e2ec53c5667b98aaa'

AUTH_USER_MODEL = 'api.User'
AUTHENTICATION_BACKENDS = ['api.auth.AuthenticationBackend']
ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = '4960Qn9GFLgj'

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@mg.getrealation.com'
EMAIL_HOST_PASSWORD = '157e5e6334067618386b4ecb2e4dcbb9'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMINS = [('Matthew Gaba', 'server_errors@getrealation.com')]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'api.apps.ApiConfig',
    'messaging.apps.MessagingConfig',
    'matchmaking.apps.MatchmakingConfig',
    'RealServer.apps.RealServerConfig',

    'rest_framework',
    'rest_framework.authtoken',
    'django_nose',
    'django_celery_results'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'RealServer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RealServer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'realserver_db',
        'USER': 'realuser',
        'PASSWORD': 'realpassword',
        'HOST': '',
        'PORT': '',
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'mediafiles/')
MEDIA_URL = '/media/'
STATIC_ROOT =  os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

YELP_APP_ID = 's7-DcAMdseJJmTHuki81Wg'
YELP_APP_SECRET = '47MsTO8LaxzsiU6JK5shKlmMyhXd70a6StGBmsM5CR1xJn9WL9WbzXEdYyzmfYCX'
#YELP_ACCESS_TOKEN = 'dJ9QyD40Ng_g7WW9bB_1BOQz1IG-rP6LIeLomkzhmapA0Dtpv7Q6UeuUw9fpqj5GdJON9cqxQdF2BWEfCBFJoBK1swOYjAh5VUxxXvrQIeal86jxuUNMi6bNDsltWHYx'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

CELERY_BROKER_URL = os.environ.get("CLOUDAMQP_URL", "amqp://")
CELERY_BROKER_POOL_LIMIT = 1
CELERY_BROKER_CONNECTION_MAX_RETRIES = None
CELERY_BROKER_HEARTBEAT = None
CELERY_BROKER_CONNECTION_TIMEOUT = 30
CELERY_RESULT_BACKEND = None
CELERY_SEND_EVENTS = False
CELERY_EVENT_QUEUE_EXPIRES = 60

CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json", "msgpack"]

FCM_SERVER_API_KEY = 'AAAACICKAlU:APA91bF_gpPDuMgn2oYRKGhZjiWH6Ra9exJERXZv4vtuRyRwJ4GTB3wuhKPW6YI0t6wMZ3Nn7Tl38Ue4LKGKeHWjuXT1AaahgC1dbLWCCHKwOwTF7ozBgV17RB2hUUQFLVEXhGzy5ZMV'

MAPBOX_API_KEY = 'pk.eyJ1IjoibWF0dGhld2dhYmEiLCJhIjoiY2l6cjlkenV6MDAzcjMzcGdjNWl0dWRyNSJ9.0DjNLfMu4xQrsO3QYcR3qw'