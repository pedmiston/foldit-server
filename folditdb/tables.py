"""MySQL database table design."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PDBFile(Base):
    """A pdbfile is created from a dump of irdata fields."""
    __tablename__ = 'pdbfile'
    pdbfile_id = Column(Integer(), primary_key=True)
    filename = Column(String(150), unique=True, index=True)
    solution_type = Column(String(10))
    data = Column(Text())

class Competition(Base):
    """A competition is a team competing in a particular puzzle."""
    __tablename__ = 'competition'
    competition_id = Column(Integer(), primary_key=True, autoincrement=True)
    team_id = Column(Integer(), ForeignKey('team.team_id'), primary_key=True)
    puzzle_id = Column(Integer(), ForeignKey('puzzle.puzzle_id'), primary_key=True)
    team = relationship('Team')
    puzzle = relationship('Puzzle')

class Puzzle(Base):
    __tablename__ = 'puzzle'
    # Use PID from IRData as puzzle_id, so don't autoincrement
    puzzle_id = Column(Integer(), primary_key=True, autoincrement=False)
    competitions = relationship('Competition')

    def __repr__(self):
        return 'Puzzle(puzzle_id=%s)' % (self.puzzle_id, )

class Team(Base):
    """A team is collection players."""
    __tablename__ = 'team'
    # Overrides team id that could be parsed from PDL strings
    team_id = Column(Integer(), primary_key=True, autoincrement=True)
    team_name = Column(String(60), primary_key=True)
    team_type = Column(String(20))
    competitions = relationship('Competition')
    players = relationship('Player')

    def __repr__(self):
        return 'Team(team_id=%s, team_name="%s", team_type="%s")' % (self.team_id, self.team_name, self.team_type)

class Submission(Base):
    """A submission is a solution submitted to a competition."""
    __tablename__ = 'submission'
    # Overrides SID in IRData
    submission_id = Column(Integer(), primary_key=True)
    competition_id = Column(Integer(), ForeignKey('competition.competition_id'))
    solution_id = Column(Integer(), ForeignKey('solution.solution_id'))
    timestamp = Column(DateTime(), nullable=False)

    player_actions = relationship('PlayerActions')

    def __repr__(self):
        return 'Submission(submission_id=%s, competition_id=%s, solution_id=%s, timestamp="%s")' % (self.submission_id, self.competition_id, self.solution_id, self.timestamp)

class TopSubmission(Base):
    """A top submission is a submission with rank information."""
    __tablename__ = 'top_submission'
    submission_id = Column(Integer(), ForeignKey('submission.submission_id'), primary_key=True)
    rank_type = Column(String(10), nullable=False)
    rank = Column(Integer(), nullable=False)

class Solution(Base):
    """A solution is a molecule with a particular history."""
    __tablename__ = 'solution'
    solution_id = Column(Integer(), primary_key=True)
    molecule_id = Column(Integer(), ForeignKey('molecule.molecule_id'))
    history_id = Column(Integer(), ForeignKey('history.history_id'))

class History(Base):
    """A history is a sequence of edits."""
    __tablename__ = 'history'
    history_id = Column(Integer(), primary_key=True)
    history_hash = Column(String(64), unique=True)
    total_moves = Column(Integer())
    edits = relationship('Edit')

class Edit(Base):
    """An edit is a change from one molecule to another."""
    __tablename__ = 'edit'
    edit_id = Column(Integer(), primary_key=True)
    history_id = Column(Integer(), ForeignKey('history.history_id'))
    molecule_id = Column(Integer(), ForeignKey('molecule.molecule_id'))
    prev_molecule_id = Column(Integer(), ForeignKey('molecule.molecule_id'))
    moves = Column(Integer())
    edit_n = Column(Integer())

class Molecule(Base):
    """A molecule is a solution with a score."""
    __tablename__ = 'molecule'
    molecule_id = Column(Integer(), primary_key=True, autoincrement=True)
    molecule_hash = Column(String(40), primary_key=True)
    score = Column(Float(precision=32))

class Player(Base):
    """A player is a member of a team."""
    __tablename__ = 'player'
    player_id = Column(Integer(), primary_key=True, autoincrement=True)
    player_name = Column(String(60), primary_key=True)
    team_id = Column(Integer(), ForeignKey('team.team_id'))

    player_actions = relationship('PlayerActions')

class PlayerActions(Base):
    """A player action is an action made by a player."""
    __tablename__ = 'player_actions'
    player_actions_id = Column(Integer(), primary_key=True)
    submission_id = Column(Integer(), ForeignKey('submission.submission_id'))
    player_id = Column(Integer(), ForeignKey('player.player_id'))
    action_id = Column(Integer(), ForeignKey('action.action_id'))
    action_n = Column(Integer())

class Action(Base):
    """An action is an operation performed to generate solutions."""
    __tablename__ = 'action'
    action_id = Column(Integer(), primary_key=True)
    action_name = Column(String(55))
