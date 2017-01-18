from settings.common import *

INSTALLED_APPS += ('storages',)
AWS_STORAGE_BUCKET_NAME = 'realdatingbucket'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'realserverdb',
        'USER' : 'realuser',
        'PASSWORD' : 'lWnhV3iTlv0G',
        'HOST' : 'realserverdb.csar4iwgsjzp.us-west-2.rds.amazonaws.com',
        'PORT' : '5432',
    }
}