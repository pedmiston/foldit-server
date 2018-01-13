from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .tables import Base

# Initialize DB engine
# pool_pre_ping: Test connection before transacting
DB = create_engine(environ['MYSQL_FOLDIT_DB'], pool_pre_ping=True)

# Create a class that creates new sessions
Session = sessionmaker()
Session.configure(bind=DB)

# Create tables that do not exist yet
# Base.metadata.create_all(DB)
