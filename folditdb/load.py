import logging

from sqlalchemy import exists

from . import tables
from .irdata import IRData, group_pdls_by_player, IRDataCreationError

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
        exists().where(tables.PDBFile.filename == irdata.filename)
    ).scalar()
    if pdb_file_exists:
        logger.info('pdb file already exists in the db: %s', irdata.filename)
        return

    pdb_file = tables.PDBFile(
        filename=irdata.filename,
        solution_type=irdata.solution_type,
        data=irdata.data,
    )
    session.add(pdb_file)

    molecule = tables.Molecule(
        molecule_hash=irdata.molecule_hash,
        score=irdata.score,
    )
    session.add(molecule)

    history = tables.History(
        history_hash=irdata.history_hash,
        total_moves=irdata.total_moves,
    )
    session.add(history)

    puzzle = tables.Puzzle(puzzle_id=irdata.puzzle_id)
    puzzle = session.merge(puzzle)
    session.commit()

    team = tables.Team(
        team_name=irdata.team_name,
        team_type=irdata.team_type,
    )
    team = session.merge(team)
    session.commit()

    competition = tables.Competition(
        team_id=team.team_id,
        puzzle_id=puzzle.puzzle_id,
    )
    competition = session.merge(competition)
    session.merge(competition)

    solution = tables.Solution(
        molecule_id=molecule.molecule_id,
        history_id=history.history_id,
    )
    session.add(solution)
    session.commit()

    submission = tables.Submission(
        competition_id=competition.competition_id,
        solution_id=solution.solution_id,
        timestamp=irdata.timestamp,
    )
    session.add(submission)
    session.commit()

    if irdata.solution_type == 'top':
        top_submission = tables.TopSubmission(
            submission_id = submission.submission_id,
            rank_type = irdata.rank_type,
            rank = irdata.rank,
        )
        session.add(top_submission)

    prev_molecule = None
    for edit_info in irdata.history_string.split(','):
        try:
            molecule_hash, moves_str = edit_info.split(':')
        except ValueError:
            raise IRDataPropertyError('edit does not contain molecule hash and moves, %s' % edit_info)

        try:
            moves = int(moves_str)
        except TypeError:
            raise IRDataPropertyError('moves not an int, %s' % edit_info)

        molecule = tables.Molecule(molecule_hash=molecule_hash)
        molecule = session.merge(molecule)
        session.commit()

        if prev_molecule is not None:
            edit = tables.Edit(
                history_id=history.history_id,
                molecule_id=molecule.molecule_id,
                prev_molecule_id=prev_molecule.molecule_id,
                moves=moves
            )
            session.add(edit)

        prev_molecule = molecule

    session.commit()

    for pdl in group_pdls_by_player(irdata.pdl_strings):
        player = tables.Player(player_name=pdl.player_name,
                               team_id=team.team_id)
        player = session.merge(player)
        session.commit()

        for action_name, action_n in pdl.actions.items():
            action = tables.Action(action_name=action_name)
            action = session.merge(action)
            session.commit()

            player_action = tables.PlayerActions(
                player_id=player.player_id,
                action_id=action.action_id,
                action_n=action_n,
            )
            session.add(player_action)

    session.commit()

    if local_session:
        session.close()
