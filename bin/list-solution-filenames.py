#!/usr/bin/env python
# list-solution-filenames.py lists the solution filenames within a json file.
# Usage: list-solution-filenames [JSON_DATA_FILE]
import os
import sys
import json
from os import environ
from pathlib import Path
import boto3

def list_solutions_in_file(filename):
    filename = Path(filename)
    assert filename.exists(), "json file doesn't exist"

    with filename.open() as f:
      for j in f:
          try:
              d = json.loads(j)
              s = d['FILEPATH']
          except Exception as e:
              sys.stderr.write("error extracting FILEPATH: "+e)
          else:
              sys.stdout.write(s+'\n')

def list_solutions_in_bucket(bucket):
    client = new_s3_session()
    resp = client.list_objects_v2(Bucket='foldit')
    keys = [obj['Key'] for obj in resp['Contents']]
    for key in keys:
        client.download_file('foldit', key, key)
        list_solutions_in_file(key)
        os.remove(key)

def new_s3_session():
    session = boto3.session.Session()
    client = session.client('s3',
                            aws_access_key_id=environ['AWS_ACCESS_KEY'],
                            aws_secret_access_key=environ['AWS_SECRET_KEY'])
    return client

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('-b', '--bucket',
                        help='interpret [name] as the name of a bucket',
                        action='store_true')
    args = parser.parse_args()
    if args.bucket:
        list_solutions_in_bucket(args.name)
    else:
        list_solutions_in_file(args.name)
