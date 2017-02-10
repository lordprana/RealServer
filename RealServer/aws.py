import boto3
import random
import string
import os
import json
import re
from boto.s3.connection import S3Connection, Bucket, Key

def s3_generate_presigned_post(file_type, user, file_name=None):
  os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAI4755USWAQYAFTUA'
  os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
  os.environ['S3_BUCKET'] = 'realdatingbucket'

  S3_BUCKET = os.environ.get('S3_BUCKET')

  # Generate a random name for the file

  if not file_name:
    file_name = user.pk + '/' +  ''.join(random.choice(string.lowercase) for i in range(12))
  s3 = boto3.client('s3')

  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })

def s3_delete_file(url_to_file):
  AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
  AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
  S3_BUCKET = os.environ.get('S3_BUCKET')

  conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
  b = Bucket(conn, S3_BUCKET)
  k = Key(b)

  file_path = re.search(r'\.com/(.*)', url_to_file).group(1)

  k.key = file_path
  b.delete_key(k)
