import sqlalchemy
from sqlalchemy.orm import sessionmaker
from irdata import IRData
from db import Base, Score

from util import get_from_vault

url = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
engine = sqlalchemy.create_engine(url.format(
    user='foldittest',
    password=get_from_vault('mysql_foldit_password'),
    host='192.241.128.175',
    port='3306',
    dbname='FolditTest',
))
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)

def test_extract_scores_from_single_solution():
    data = dict(HISTORY='1,2,3', SCORE='134.2')
    irdata = IRData(data)
    solution_scores = irdata.solution_scores()
    assert len(solution_scores) == 2
    assert solution_scores[0] == '3'
    assert solution_scores[1] == 134.2

def test_put_scores_in_db():
    s = Session()
    data = dict(HISTORY='1,2,3', SCORE='134.2')
    irdata = IRData(data)
    score = irdata.to_score_obj()
    s.add(score)
    s.commit()

    results = s.query(Score)
    assert len(results.all()) == 1
    score_2 = results.first()
    assert score == score_2

    s.delete(score)
    s.commit()
    s.close()
