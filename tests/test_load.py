import logging

import pytest

import folditdb
from folditdb import tables

# Configure program logger to log to file
LOG_FILEPATH = 'load.py.log'
logger = logging.getLogger('folditdb')
handler = logging.FileHandler(LOG_FILEPATH)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(message)s',
                              datefmt='%m/%d/%Y %I:%M%p')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def test_load(session):
    json_str = open('tests/test_data/top_solution.json').read()
    folditdb.load_from_json(json_str, session)

    molecule_hash = '136a3a4a-d2ee-44f6-843e-f5878af8d6c9'
    molecule = (session.query(tables.Molecule)
                       .filter_by(molecule_hash=molecule_hash)
                       .first())
    assert molecule.score == 10576.88
