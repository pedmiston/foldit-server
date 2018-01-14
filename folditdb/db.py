from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Initialize DB engine
# pool_pre_ping: Test connection before transacting
# pool_timeout: Number of seconds to wait per connection
DB = create_engine(environ['MYSQL_FOLDIT_DB'],
                   pool_pre_ping=True,
                   pool_timeout=3600)

# Create a class that creates new sessions
Session = sessionmaker()
Session.configure(bind=DB)
