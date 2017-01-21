import boto3
import random
import string
import os
import json

def s3_generate_presigned_post(file_type, user):
  S3_BUCKET = os.environ.get('S3_BUCKET')
  print S3_BUCKET

  # Generate a random name for the file

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