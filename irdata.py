import json

class IRData:
    def __init__(self, data):
        self._data = data

    @property
    def filename(self):
        return self._data['FILENAME']

    @property
    def solution_id(self):
        if 'HISTORY' not in self._data:
            raise InvalidSolutionError
        return self._data['HISTORY'].split(',')[-1]

    @property
    def solution_score(self):
        if 'SCORE' not in self._data:
            raise InvalidSolutionError
        score = self._data['SCORE']
        try:
            score = float(score)
        except ValueError:
            raise InvalidSolutionError
        return score

    def solution_scores(self):
        return [self.solution_id, self.solution_score]


class InvalidSolutionError(Exception):
    """Something's not right with this solution."""
