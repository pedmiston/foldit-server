from os import environ, remove

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pytest

from folditdb.tables import Base
from folditdb.irdata import IRData


@pytest.fixture
def session():
    DB = create_engine(environ['MYSQL_FOLDIT_TEST_DB'])
    Base.metadata.create_all(DB)
    Session = sessionmaker()
    Session.configure(bind=DB)
    s = Session()
    yield s
    s.close()
    Base.metadata.drop_all(DB)
