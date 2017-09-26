#!/usr/bin/env python
import sys
from os import environ
from pathlib import Path

import boto3
from botocore.client import Config

usage = 'push.py path/to/data.json'

def parse_args():
    assert len(sys.argv) == 2, 'incorrect arguments\n'+usage
    bundle = Path(sys.argv[1])
    assert bundle.exists(), 'file does not exist'
    return bundle

def push_bundle(bundle):
    session = boto3.session.Session()
    client = session.client('s3', region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id=environ['DO_ACCESS_KEY'],
                            aws_secret_access_key=environ['DO_SECRET_KEY'])
    client.upload_file(bundle, BUCKET, bundle.name)

if __name__ == '__main__':
    bundle = parse_args()
    push_bundle(bundle)
