import logging

import pytest

import folditdb
from folditdb import tables


def test_load(session):
    json_str = open('tests/test_data/top_solution.json').read()
    folditdb.load_from_json(json_str, session)

    molecule_hash = 'v3'
    molecule = (session.query(tables.Molecule)
                       .filter_by(molecule_hash=molecule_hash)
                       .first())
    assert molecule.score == 100.99

def test_load_bad_solution(session):
    json_str = open('tests/test_data/top_solution_bad.json').read()
    with pytest.raises(IRDataPropertyError):
        folditdb.load_from_json(json_str, session, return_on_error=False)
