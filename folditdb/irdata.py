import json
import hashlib
import re
from datetime import datetime
from collections import namedtuple

re_top_solution = re.compile(r'solution_(?P<rank_type>[a-z]+)_(?P<rank>\d+)_')

class IRDataError(Exception):
    pass

class IRDataCreationError(IRDataError):
    pass

class IRDataPropertyError(IRDataError):
    pass

class PDLCreationError(IRDataError):
    pass

class PDLPropertyError(IRDataError):
    pass


class IRData:
    """IRData objects facilite the transfer of IRData to model objects.

    IRData objects are created from the data contained in a single
    solution pdb file stored on the Foldit analytics server. The
    solution pdb files were scraped with the foldit-go program command
    'scrape' and consist of all lines in the pdb file that start with
    "IRDATA".

    IRData objects store data internally as a dict, and expose
    output values used to create model objects as properties.

    > json_str = '{"FILEPATH": "/location/of/solution.pdb"}'
    > irdata = IRData.from_json(json_str)
    > irdata.filename == '/location/of/solution.pdb'

    Note that "FILEPATH" in the input is accessed as "filename" in the output.
    This allows more complicated properties to be derived from the internal
    data.

    > json_str = '{"HISTORY": "V1:10,V2:5,V3:8"}'
    > irdata = IRData.from_json(json_str)
    > irdata.history_id == 'V3'

    Properties such as "history_id" in the above example are computed
    once and cached. If a property cannot be computed, an IRDataPropertyError
    is raised.

    The reason for using IRData objects is to facilitate the translation
    of the same json data into multiple model objects without redundantly
    processing the same data.
    """
    def __init__(self, data, fill_cache=False):
        """Create an IRData object from a dict of strings."""
        self._data = data
        self._cache = {}
        if fill_cache:
            self.cache_all_properties()

    @classmethod
    def from_json(cls, json_str, **kwargs):
        """Create an IRData object from a json string."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as err:
            raise IRDataCreationError('bad JSON: %s' % err)
        else:
            return cls(data, **kwargs)

    @classmethod
    def from_file(cls, json_filepath, **kwargs):
        """Create an IRData object from a json file."""
        with open(json_filepath) as json_file:
            json_str = json_file.read()
            return cls.from_json(json_str, **kwargs)

    def __dir__(self):
        """Return names of properties to verify."""
        verified_properties = 'filename solution_type rank_type rank data puzzle_id history_string molecule_hash history_hash total_moves score timestamp pdl_strings player_pdls team_name team_type edits'.split()
        return verified_properties

    def cache_all_properties(self):
        for attr in dir(self):
            getattr(self, attr)  # fill cache

    @property
    def filename(self):
        """The full filename for the pdb solution file."""
        if 'filename' in self._cache:
            return self._cache['filename']

        filename = self._data.get('FILEPATH')
        if filename is None:
            raise IRDataPropertyError('solution has no FILEPATH')

        return self._cache.setdefault('filename', filename)

    @property
    def solution_type(self):
        """Solutions can be "top" or "regular"."""
        if 'solution_type' in self._cache:
            return self._cache['solution_type']

        if '/top/' in self.filename:
            solution_type = 'top'
        elif '/all/' in self.filename:
            solution_type = 'regular'
        else:
            msg = 'cannot determine solution type from filename: filename="%s"'
            raise IRDataPropertyError(msg % self.filename)

        return self._cache.setdefault('solution_type', solution_type)

    @property
    def rank_type(self):
        if 'rank_type' in self._cache:
            return self._cache['rank_type']

        try:
            rank_type = re_top_solution.search(self.filename).group(1)
        except AttributeError:
            msg = 'unable to parse rank_type from filename, filename="%s"'
            raise IRDataPropertyError(msg % self.filename)

        return self._cache.setdefault('rank_type', rank_type)

    @property
    def rank(self):
        if 'rank' in self._cache:
            return self._cache['rank']

        try:
            rank_str = re_top_solution.search(self.filename).group(2)
            rank = int(rank_str)
        except AttributeError:
            msg = 'unable to parse rank from filename, filename="%s"'
            raise IRDataPropertyError(msg % self.filename)

        return self._cache.setdefault('rank', rank)

    @property
    def data(self):
        if 'data' in self._cache:
            return self._cache['data']

        return self._cache.setdefault('data', json.dumps(self._data))

    @property
    def puzzle_id(self):
        if 'puzzle_id' in self._cache:
            return self._cache['puzzle_id']

        pid_str = self._data.get('PID')
        if pid_str is None:
            msg = 'solution has no PID: filename="%s"'
            raise IRDataPropertyError(msg % self.filename)

        try:
            puzzle_id = int(pid_str)
        except ValueError:
            msg = 'PID is not an int: PID="%s"'
            raise IRDataPropertyError(msg % pid_str)

        return self._cache.setdefault('puzzle_id', puzzle_id)

    @property
    def history_string(self):
        if 'history_string' in self._cache:
            return self._cache['history_string']

        history_string = self._data.get('HISTORY')
        if history_string is None:
            msg = 'solution has no HISTORY: filename="%s"'
            raise IRDataPropertyError(msg % self.filename)

        return self._cache.setdefault('history_string', history_string)

    @property
    def molecule_hash(self):
        if 'molecule_hash' in self._cache:
            return self._cache['molecule_hash']

        # Does not fail if history_string is a string
        last_move_in_history = self.history_string.split(',')[-1]
        try:
            molecule_hash, _ = last_move_in_history.split(':')
        except ValueError:
            msg = 'unable to parse history: history_string="%s"'
            raise IRDataPropertyError(msg % self.history_string)

        return self._cache.setdefault('molecule_hash', molecule_hash)

    @property
    def history_hash(self):
        if 'history_hash' in self._cache:
            return self._cache['history_hash']

        history_hash = hashlib.sha256(self.history_string.encode('utf-8')).hexdigest()
        return self._cache.setdefault('history_hash', history_hash)

    @property
    def total_moves(self):
        if 'total_moves' in self._cache:
            return self._cache['total_moves']

        try:
            moves = [int(pair.split(':')[1])
                     for pair in self.history_string.split(',')]
        except (IndexError, ValueError, TypeError):
            msg = 'unable to parse moves from history: history_string="%s"'
            raise IRDataPropertyError(msg % self.history_string)
        else:
            total_moves = sum(moves)

        if total_moves == 0:
            msg = 'no moves were read from history string, history_string="%s"'
            raise IRDataPropertyError(msg % self.history_string)

        return self._cache.setdefault('total_moves', total_moves)

    @property
    def score(self):
        if 'score' in self._cache:
            return self._cache['score']

        score_str = self._data.get('SCORE')
        if score_str is None:
            msg = 'solution has no SCORE: filename="%s"'
            raise IRDataPropertyError(msg % self.filename)

        try:
            score = float(score_str)
        except ValueError:
            msg = 'SCORE is not a float: score_str="%s"'
            raise IRDataPropertyError(msg % score_str)

        return self._cache.setdefault('score', score)

    @property
    def timestamp(self):
        if 'timestamp' in self._cache:
            return self._cache['timestamp']

        timestamp_str = self._data.get('TIMESTAMP')
        if timestamp_str is None:
            raise IRDataPropertyError('solution has no TIMESTAMP: filename="%s"' % self.filename)

        try:
            timestamp_int = int(timestamp_str)
        except ValueError:
            raise IRdataPropertyError('timestamp not an int: timestamp_str="%s"' % timestamp_str)

        timestamp = datetime.fromtimestamp(timestamp_int)
        return self._cache.setdefault('timestamp', timestamp)

    @property
    def pdl_strings(self):
        if 'pdl_strings' in self._cache:
            return self._cache['pdl_strings']

        pdl_strings = self._data.get('PDL')
        if pdl_strings is None:
            raise IRDataPropertyError('solution has no PDLs: filename="%s"' % self.filename)

        if not isinstance(pdl_strings, list):
            pdl_strings = [pdl_strings, ]

        pdl_strings = [purify(pdl_str) for pdl_str in pdl_strings]

        return self._cache.setdefault('pdl_strings', pdl_strings)

    @property
    def player_pdls(self):
        if 'player_pdls' in self._cache:
            return self._cache['player_pdls']

        players = {}

        for pdl_string in self.pdl_strings:
            pdl = PDL.from_string(pdl_string)
            if pdl.player_name in players:
                players[pdl.player_name].merge_player_actions(pdl)
            else:
                players[pdl.player_name] = pdl

        return self._cache.setdefault('player_pdls', players.values())

    @property
    def team_name(self):
        if 'team_name' in self._cache:
            return self._cache['team_name']

        pdls = [PDL.from_string(pdl_str) for pdl_str in self.pdl_strings]
        team_names = set(pdl.team_name for pdl in pdls)

        if len(team_names) != 1:
            msg = 'more than one team in pdl, pdl_strings="%s"'
            raise IRDataPropertyError(msg % self.pdl_strings)

        return self._cache.setdefault('team_name', team_names.pop())

    @property
    def team_type(self):
        if 'team_type' in self._cache:
            return self._cache['team_type']

        if self.team_name.startswith('soloist'):
            team_type = 'soloist'
        else:
            team_type = 'evolver'

        return self._cache.setdefault('team_type', team_type)

    @property
    def edits(self):
        if 'edits' in self._cache:
            return self._cache['edits']

        Edit = namedtuple('Edit', ['molecule_hash', 'moves'])
        edits = []
        for edit_info in self.history_string.split(','):
            try:
                molecule_hash, moves_str = edit_info.split(':')
            except ValueError:
                raise IRDataPropertyError('edit does not contain molecule hash and moves, %s' % edit_info)

            try:
                moves = int(moves_str)
            except TypeError:
                raise IRDataPropertyError('moves not an int, %s' % edit_info)
            edits.append(Edit(molecule_hash, moves))

        return self._cache.setdefault('edits', edits)


class PDL:
    """PDL objects contain data for the people contributing a solution.

    PDL objects are derivatives of IRData objects. PDL objects are
    separate from IRData objects because each IRData object may
    have one or more PDLs associated with it.

    PDL data is used to create model objects for players and teams, as well as
    for the action log of moves made by each player.
    """
    def __init__(self, data):
        self._data = data
        self._cache = {}

    @classmethod
    def from_string(cls, pdl_str):
        data = {}

        if re.match('^\.* ', pdl_str):
            pdl_str = pdl_str.strip('^\.* ')
        else:
            msg = 'unable to parse PDL: pdl_str="%s"'
            raise PDLCreationError(msg % pdl_str)

        fields = pdl_str.split(',')
        player_name, team_name = fields[:2]

        # Assign each soloist to their own team name
        if team_name == '[no group]':
            team_name = 'soloist-%s' % player_name

        try:
            player_id, team_id = map(int, fields[2:4])
        except ValueError:
            msg = 'unable to convert player_id and team_id to ints, pdl_str="%s"'
            raise PDLCreationError(msg % pdl_str)

        data = dict(
            player_name=player_name,
            team_name=team_name,
            player_id=player_id,
            team_id=team_id,
            pdl_str=pdl_str
        )
        return cls(data)

    def merge_player_actions(self, other):
        for action_name, action_n in other.actions.items():
            if action_name in self.actions:
                self.actions[action_name] += action_n
            else:
                self.actions[action_name] = action_n

    @property
    def pdl_str(self):
        return self._data['pdl_str']

    @property
    def team_type(self):
        if 'team_type' in self._cache:
            return self._cache['team_type']

        if self._data['team_name'].startswith('soloist'):
            team_type = 'soloist'
        else:
            team_type = 'evolver'

        return self._cache.setdefault('team_type', team_type)

    @property
    def actions(self):
        if 'actions' in self._cache:
            return self._cache['actions']

        actions = {}
        try:
            action_str = self.pdl_str.split('LOG:')[1].strip()
        except IndexError:
            msg = 'unable to parse actions from pdl str, pdl_str="%s"'
            raise PDLPropertyError(msg % self.pdl_str)

        for x in action_str.replace('|', '').split():
            try:
                action_name, action_n_str = x.split('=')
            except ValueError:
                action_name = x
                action_n_str = '0'

            if action_name == '':
                action_name = 'UnknownAction'

            try:
                action_n = int(action_n_str)
            except ValueError:
                msg = 'action n is not an int: action_n_str="%s"'
                raise PDLPropertyError(msg % action_n_str)

            if action_name in actions:
                actions[action_name] += action_n
            else:
                actions[action_name] = action_n

        self._cache['actions'] = actions
        return actions

    def __getattr__(self, key):
        return self._data.get(key)


def purify(s):
    return str(s.encode('latin-1', 'ignore').decode('latin-1'))
