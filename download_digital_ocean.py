#!/usr/bin/env python
from os import environ
import boto3

session = boto3.session.Session()
client = session.client('s3',
                        region_name='nyc3',
                        endpoint_url='https://nyc3.digitaloceanspaces.com',
                        aws_access_key_id=environ['DO_ACCESS_KEY'],
                        aws_secret_access_key=environ['DO_SECRET_KEY'])
resp = client.list_objects_v2(Bucket='foldit')
keys = [obj['Key'] for obj in resp['Contents']]
for key in keys:
    print('downloading: {}'.format(key))
    client.download_file('foldit', key, 'digital-ocean/' + key)
