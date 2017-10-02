import yaml
from minio import Minio
from minio.error import ResponseError

auth = yaml.load(open('secrets.yml'))
client = Minio('s3.amazonaws.com',
               access_key=auth['do_access_key'],
               secret_key=auth['do_secret_key'],
               secure=True)

for bucket in client.list_buckets():
    print(bucket.name, bucket.creation_date)
