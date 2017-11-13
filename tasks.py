from os import environ
import boto3
import botocore
from invoke import task

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

def new_s3_session():
    session = boto3.session.Session()
    client = session.client('s3',
                            aws_access_key_id=environ['AWS_ACCESS_KEY'],
                            aws_secret_access_key=environ['AWS_SECRET_KEY'])
    return client
