import sys
import json
import csv
import time
from pathlib import Path
import os
from os import environ
import boto3
import botocore
from invoke import task
import folditdb

BUCKET = 'foldit'


@task
def load_key(ctx, key):
    session = new_s3_session()
    if not Path(key).exists():
        _get_key(key, session)
    _load_key(key, session)

@task
def load_all_keys(ctx):
    session = new_s3_session()
    keys = _list_keys(session)
    for key in keys:
        if not Path(key).exists():
            _get_key(key, session)
        _load_key(key, session)
        os.remove(key)

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
    t = get_time()
    print(f'[{t}] downloading key "{key}"...')

    if dst is not None:
        dst = Path(dst, key)
    else:
        dst = key

    try:
        session.download_file(BUCKET, key, dst)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(f'Object "{key}" does not exist in bucket "{BUCKET}"')
        else:
            raise

def _load_key(key, session):
    t = get_time()
    print(f'[{t}] loading key "{key}"...')
    folditdb.load_solutions_from_file(key)


def get_time():
    return time.strftime('%H:%M:%S', time.localtime())
