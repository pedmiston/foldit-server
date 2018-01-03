import sys
import json
import csv
from pathlib import Path
from os import environ
import boto3
import botocore
from invoke import task

BUCKET = 'foldit'


@task
def list_keys(ctx):
    """List all keys in an S3 bucket."""
    session = new_s3_session()
    keys = _list_keys(session)
    print('\n'.join(keys))

@task
def get_key(ctx, key):
    """Download a file from an S3 bucket."""
    session = new_s3_session()
    _get_key(key, session)

@task
def get_all_keys(ctx, dst):
    """Download all keys in an S3 bucket."""
    session = new_s3_session()
    keys = _list_keys(session)

    dst = Path(dst)
    if not dst.is_dir():
        dst.mkdir()

    for key in keys:
        _get_key(key, session, dst)

def new_s3_session():
    session = boto3.session.Session()
    client = session.client('s3',
                            aws_access_key_id=environ['AWS_ACCESS_KEY'],
                            aws_secret_access_key=environ['AWS_SECRET_KEY'])
    return client

def _list_keys(session):
    resp = session.list_objects_v2(Bucket=BUCKET)
    keys = [obj['Key'] for obj in resp['Contents']]
    return keys

def _get_key(key, session, dst=None):
    if dst is not None:
        dst = Path(dst, key)
    else:
        dst = key

    try:
        client.download_file(BUCKET, key, dst)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(f'Object "{key}" does not exist in bucket "{BUCKET}"')
        else:
            raise
