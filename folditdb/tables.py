"""MySQL database table design."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PDBFile(Base):
    """A pdbfile is created from a dump of irdata fields."""
    __tablename__ = 'pdbfile'
    pdbfile_id = Column(Integer(), primary_key=True)
    filename = Column(String(100), unique=True, index=True)
    solution_type = Column(String(10))
    data = Column(Text())

class Competition(Base):
    """A competition is a team competing in a particular puzzle."""
    __tablename__ = 'competition'
    competition_id = Column(Integer(), primary_key=True)
    team_id = Column(Integer(), ForeignKey('team.team_id'))
    puzzle_id = Column(Integer(), ForeignKey('puzzle.puzzle_id'))

class Submission(Base):
    """A submission is a solution submitted to a competition."""
    __tablename__ = 'submission'
    submission_id = Column(Integer(), primary_key=True)
    competition_id = Column(Integer(), ForeignKey('competition.competition_id'))
    solution_id = Column(Integer(), ForeignKey('solution.solution_id'))
    timestamp = Column(DateTime(), nullable=False)

    player_actions = relationship('PlayerActions')

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

class Molecule(Base):
    """A molecule is a solution with a score."""
    __tablename__ = 'molecule'
    molecule_id = Column(Integer(), primary_key=True)
    molecule_hash = Column(String(40), unique=True)
    score = Column(Float())

class Team(Base):
    """A team is collection players."""
    __tablename__ = 'team'
    team_id = Column(Integer(), primary_key=True)
    team_name = Column(String(60), unique=True, index=True)
    team_type = Column(String(20))

    players = relationship('Player')

class Player(Base):
    """A player is a member of a team."""
    __tablename__ = 'player'
    player_id = Column(Integer(), primary_key=True)
    player_name = Column(String(60), unique=True, index=True)
    team_id = Column(Integer(), ForeignKey('team.team_id'))

class PlayerActions(Base):
    """A player action is an action made by a player."""
    __tablename__ = 'player_actions'
    player_id = Column(Integer(), ForeignKey('player.player_id'))
    action_id = Column(Integer(), ForeignKey('action.action_id'))
    action_n = Column(Integer())

class Action(Base):
    """An action is an operation performed to generate solutions."""
    __tablename__ = 'action'
    action_id = Column(Integer(), primary_key=True)
    action_name = Column(String(55))