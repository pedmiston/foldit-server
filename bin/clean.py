#!/usr/bin/env python
from os import environ
from sqlalchemy import create_engine
from folditdb.tables import Base

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--real', action='store_true')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

if args.real:
    print('Cleaning the real database')
    DB = create_engine(environ['MYSQL_FOLDIT_DB'])
    Base.metadata.drop_all(DB)

if args.test:
    print('Cleaning the test database')
    DB = create_engine(environ['MYSQL_FOLDIT_TEST_DB'])
    Base.metadata.drop_all(DB.connect())

if not any((args.real, args.test)):
    print('Error: nothing cleaned!\n')
    parser.print_help()
