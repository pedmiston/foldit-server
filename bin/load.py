#!/usr/bin/env python
# Usage:
# $ load.py --list
# $ load.py --download-only '1510387305.json'
# $ load.py --filter-only '1510387305.json'
# $ load.py '1510387305-top.json'

import argparse
import subprocess
import sys
import logging
from os import environ, stat, remove
from pathlib import Path

import boto3
import botocore

import folditdb

# Name of S3 bucket holding scrape files
BUCKET = 'foldit'

# Configure program logger
logger = logging.getLogger(__name__)
handler = logging.FileHandler('load.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M %p')
handler.setFormatter(formatter)
logger.addHandler(handler)

# File storing which keys have been loaded
loaded_keys_filepath = 'loaded-keys.txt'


def new_s3_session():
    session = boto3.session.Session()
    client = session.client('s3',
                            aws_access_key_id=environ['AWS_ACCESS_KEY'],
                            aws_secret_access_key=environ['AWS_SECRET_KEY'])
    return client


def list_keys():
    session = new_s3_session()
    resp = session.list_objects_v2(Bucket=BUCKET)
    keys = [obj['Key'] for obj in resp['Contents']]
    return keys


def get_top_solutions(key):
    scrape_file = Path(key)
    top_solutions_file = Path('{}-top.json'.format(scrape_file.stem))

    if not top_solutions_file.exists():
        if not scrape_file.exists():
            get_key(key)

        filter_top_solutions(scrape_file, top_solutions_file)

        remove(scrape_file)

    return top_solutions_file


def get_key(key):
    session = new_s3_session()
    dst = key
    logger.info('Downloading key=%s' % key)
    try:
        session.download_file(BUCKET, key, dst)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print('Key %s not found in bucket %s' % key, BUCKET)
            sys.exit()


def filter_top_solutions(scrape_file, top_solutions_file):
    cmd = 'bin/filter-top-bid-solutions {} > {}'.format(scrape_file, top_solutions_file)
    p = subprocess.Popen(cmd, shell=True)
    logger.info('Filtering top solutions %s', top_solutions_file)
    p.communicate()


def key_has_been_loaded(key):
    if not Path(loaded_keys_filepath).exists():
        return False

    with open(loaded_keys_filepath, 'r') as f:
        keys = [l.strip() for l in f.readlines()]

    return key in keys


def save_key_to_loaded_keys_file(key):
    with open(loaded_keys_filepath, 'a') as f:
        f.write(key + '\n')


def load_key(key):
    top_solutions_file = get_top_solutions(key)

    top_solutions_file_is_empty = (stat(top_solutions_file).st_size == 0)
    if top_solutions_file_is_empty:
        logger.info('No top solutions were extracted from key %s', key)
    else:
        logger.info('Loading solutions into db %s', top_solutions_file)
        folditdb.load_top_solutions_from_file(top_solutions_file)

    save_key_to_loaded_keys_file(key)
    remove(key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('key', nargs='?')
    parser.add_argument('--list', '-l', action='store_true')

    args = parser.parse_args()

    # Always log
    if True:
        logger.setLevel(logging.INFO)
        folditdb.log.use_logging('folditdb.log')

    if args.list:
        print('\n'.join(list_keys()))
        sys.exit()

    if args.key is None:
        parser.print_help()
        sys.exit()

    if args.key == 'all':
        keys = list_keys()
    else:
        keys = [args.key, ]

    for key in keys:
        if key_has_been_loaded(args.key):
            logger.info('Key %s has already been loaded', args.key)
            continue

        load_key(key)
