import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float

from util import get_from_vault

Base = declarative_base()

class Score(Base):
    __tablename__ = 'Scores'
    id = Column(String(60), primary_key=True, nullable=False)
    score = Column(Float)

url = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
engine = sqlalchemy.create_engine(url.format(
    user='foldit',
    password=get_from_vault('mysql_foldit_password'),
    host='192.241.128.175',
    port='3306',
    dbname='Foldit',
))
Base.metadata.create_all(engine)
