import logging

from sqlalchemy import exists

from folditdb.irdata import IRData, group_pdls_by_player
from folditdb.db import Session
from folditdb.tables import PDBFile

logger = logging.getLogger(__name__)


def load_from_json(json_str, session=None):
    try:
        irdata = IRData.from_json(json_str)
    except IRDataCreationError as e:
        logger.info('error creating irdata: %s', e)
        return

    # Non-local session are used for testing
    local_session = (session is None)
    if local_session:
        session = Session()

    pdb_file_exists = session.query(
        exists().where(PDBFile.filename == irdata.filename)
    ).scalar()
    if pdb_file_exists:
        logger.info('pdb file already exists in the db: %s', irdata.filename)
        return

    pdb_file = PDBFile(
        filename=irdata.filename,
        solution_type=irdata.solution_type,
        data=irdata.data,
    )
    session.add(pdb_file)

    molecule = Molecule(
        molecule_hash=irdata.molecule_hash,
        score=irdata.score,
    )
    session.add(molecule)

    history = History(
        history_hash=irdata.history_hash,
        total_moves=irdata.total_moves,
    )
    session.add(history)

    puzzle = Puzzle(puzzle_id=irdata.puzzle_id)
    puzzle = session.merge(puzzle)

    solution = Solution(
        molecule_id=molecule.molecule_id,
        history_id=history.history_id,
    )
    session.add(solution)

    team = Team(
        team_name=irdata.team_name,
        team_type=irdata.team_type,
    )
    team = session.merge(team)

    competition = Competition(
        team_id=team.team_id,
        puzzle_id=puzzle.puzzle_id,
    )
    competition = session.merge(competition)

    submission = Submission(
        competition_id=competition.competition_id,
        solution_id=solution.solution_id,
        timestamp=irdata.timestamp,
    )
    session.add(submission)

    for edit_info in irdata.history_string.split(','):
        prev_molecule = None
        for molecule_hash, moves in edit_info.split(':'):
            molecule = Molecule(molecule_hash=molecule_hash)
            molecule = session.merge(molecule)

            if prev_molecule is not None:
                edit = Edit(
                    history_id=history.history_id
                    molecule_id=molecule.molecule_id,
                    prev_molecule_id=prev_molecule.molecule_id,
                    moves=moves
                )
                session.add(edit)

            prev_molecule = molecule

    for pdl in group_pdls_by_player(irdata.pdl_strings):
        player = Player(player_name=pdl.player_name,
                        team_id=team.team_id)
        player = session.merge(player)

        for action_name, action_n in pdl.actions.keys():
            action = Action(action_name=action_name)
            action = session.merge(action)
            player_action = PlayerActions(
                player_id=player.player_id,
                action_id=action.action_id,
                action_n=action_n,
            )
            session.add(player_action)

    session.commit()

    if local_session:
        session.close()
