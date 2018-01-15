#!/usr/bin/env python
"""Load data from files containing IRData fields scraped from PDB solution files.

Usage:
$ load.py --help
$ load.py --list-keys
$ load.py --clean-logs
$ load.py 1510387305.json
$ load.py all
"""
import argparse
import subprocess
import sys
import logging
import re
from os import environ, stat
from pathlib import Path

import boto3
import botocore

import folditdb

# Name of S3 bucket holding scrape files
BUCKET = 'foldit'
# File storing which keys have been loaded
LOADED_KEYS_FILEPATH = 'loaded-keys.txt'

# Configure program logger to log to file
LOG_FILEPATH = 'load.py.log'
logger = logging.getLogger('folditdb')
handler = logging.FileHandler(LOG_FILEPATH)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(message)s',
                              datefmt='%m/%d/%Y %I:%M%p')
handler.setFormatter(formatter)
logger.addHandler(handler)


def load_key(key):
    """Load a scrape file from a key in an S3 bucket into the database."""
    if key_has_been_loaded(key):
        logger.info('key has already been loaded, key=%s', key)
        return

    try:
        local_key = get_local_key(key)
    except FileNotFoundError as e:
        logger.error('unable to download key file, %s', e)
        return

    loaded = 0
    for json_str in filter_top_solutions_with_histories(local_key):
        try:
            folditdb.load_from_json(json_str, n_tries=4)
        except Exception as err:
            logger.info('caught an error, failing out. err=%s', err)
            raise
        loaded += 1

    logger.info('loaded %s solutions in file %s', i, local_key)
    save_key_as_loaded(key)
    remove(key)


def key_has_been_loaded(key):
    """Check if this key has already been loaded."""
    if not Path(LOADED_KEYS_FILEPATH).exists():
        msg = 'file with loaded keys does not exist, loaded_keys_filepath="%s"'
        logger.info(msg, LOADED_KEYS_FILEPATH)
        return False

    keys = [line.strip() for line in open(loaded_keys_filepath)]
    return key in keys


def get_local_key(key):
    """Download a file in an S3 bucket if it doesn't already exist."""
    if Path(key).exists():
        logger.info('key already exists locally, key="%s"', key)
        return key

    session = new_s3_session()
    logger.info('downloading file from S3, key=%s' % key)
    try:
        session.download_file(BUCKET, key, key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            raise FileNotFoundError(e)
    else:
        return key


def filter_top_solutions_with_histories(scrape_filepath):
    """Filter top solutions with histories.

    Most solutions are not top solutions, and the most common error
    in loading is a file without a history. This generator function
    only yields lines from the input file that are top solutions
    and have histories.
    """
    re_top_solution = re.compile(r'/top/solution_bid')
    re_solution_with_history = re.compile(r'"HISTORY"')

    for json_str in open(scrape_filepath):
        conditions = (re_top_solution.search(json_str),
                      re_solution_with_history.search(json_str))

        if all(conditions):
            yield json_str


def save_key_as_loaded(key):
    """Save key as new line in file with loaded keys."""
    with open(LOADED_KEYS_FILEPATH, 'a') as f:
        f.write(key + '\n')


def list_keys():
    """Return a list of keys in the S3 bucket."""
    session = new_s3_session()
    resp = session.list_objects_v2(Bucket=BUCKET)
    keys = [obj['Key'] for obj in resp['Contents']]
    return keys


def new_s3_session():
    """Create a new S3 client session."""
    session = boto3.session.Session()
    client = session.client('s3',
                            aws_access_key_id=environ['AWS_ACCESS_KEY'],
                            aws_secret_access_key=environ['AWS_SECRET_KEY'])
    return client


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('key', nargs='?', help='Key to load. Pass "all" to load all keys in bucket')
    parser.add_argument('--list-keys', '-l', action='store_true')
    parser.add_argument('--clean-log', '-c', action='store_true')

    args = parser.parse_args()

    # Turn on logging
    logger.setLevel(logging.INFO)

    if args.list_keys:
        print('\n'.join(list_keys()))
        sys.exit()

    if args.clean_log:
        print('Cleaning log file')
        subprocess.run('rm -f %s' % LOG_FILEPATH, shell=True)
        if args.key is None:
            sys.exit()

    if args.key is None:
        parser.print_help()
        sys.exit()

    if args.key == 'all':
        keys = list_keys()
    else:
        keys = [args.key, ]

    for key in keys:
        load_key(key)
