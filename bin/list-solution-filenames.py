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
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id=environ['DO_ACCESS_KEY'],
                            aws_secret_access_key=environ['DO_SECRET_KEY'])
    resp = client.list_objects_v2(Bucket='foldit')
    keys = [obj['Key'] for obj in resp['Contents']]
    for key in keys:
        sys.stderr.write('Downloading {}'.format(key))
        client.download_file('foldit', key, key)
        sys.stderr.write('Listing solutions in {}'.format(key))
        list_solutions_in_file(key)
        os.remove(key)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('json')
    parser.add_argument('-b', '--bucket', help='Bucket name',
                        action='store_true')
    args = parser.parse_args()
    if args.bucket:
        list_solutions_in_bucket(args.json)
    else:
        list_solutions_in_file(args.json)
