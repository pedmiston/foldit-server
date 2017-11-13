import sys
import json
import csv
from os import environ
import boto3
import botocore
from invoke import task

from irdata import IRData, InvalidSolutionError
from db import Score

BUCKET = 'foldit'


@task
def list_keys(ctx):
    """List all keys in S3 bucket."""
    client = new_s3_session()
    resp = client.list_objects_v2(Bucket=BUCKET)
    keys = [obj['Key'] for obj in resp['Contents']]
    print('\n'.join(keys))

@task
def get_key(ctx, key):
    """Download key from S3 bucket."""
    client = new_s3_session()
    try:
        client.download_file(BUCKET, key, key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(f'Object "{key}" does not exist in bucket "{BUCKET}"')
        else:
            raise

@task
def get_solution_scores(ctx, key):
    dst = open('solution_scores.csv', 'w', newline='')
    writer = csv.writer(dst)
    writer.writerow(['solution_id', 'solution_score'])

    with open(key, 'r') as f:
        for json_str in f:
            json_data = json.loads(json_str)
            irdata = IRData(json_data)
            try:
                writer.writerow(irdata.solution_scores())
            except InvalidSolutionError:
                sys.stderr.write(f'invalid solution: {irdata.filename}')


def new_s3_session():
    session = boto3.session.Session()
    client = session.client('s3',
                            aws_access_key_id=environ['AWS_ACCESS_KEY'],
                            aws_secret_access_key=environ['AWS_SECRET_KEY'])
    return client
