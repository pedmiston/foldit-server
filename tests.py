from irdata import IRData

def test_extract_scores_from_single_solution():
    data = dict(HISTORY='1,2,3', SCORE='134.2')
    irdata = IRData(data)
    solution_scores = irdata.solution_scores()
    assert len(solution_scores) == 2
    assert solution_scores[0] == '3'
    assert solution_scores[1] == 134.2
