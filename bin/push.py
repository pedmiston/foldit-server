#!/usr/bin/env python
"""push.py pushes a json file to a bucket in the cloud."""
import sys
from os import environ
from pathlib import Path
import boto3

usage = 'push.py path/to/data.json'
BUCKET = 'foldit'

def upload_file(bundle):
    session = boto3.session.Session()
    client = session.client('s3',
                            aws_access_key_id=environ['AWS_ACCESS_KEY'],
                            aws_secret_access_key=environ['AWS_SECRET_KEY'])
    client.upload_file(str(bundle), BUCKET, bundle.name)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', help='json data file')
    args = parser.parse_args()
    bundle = Path(args.bundle)
    assert bundle.exists(), 'json file not found'
    upload_file(bundle)
