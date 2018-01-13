import time
import logging

from sqlalchemy import exists
from sqlalchemy import exc

from . import tables
from .db import Session
from .irdata import IRData, IRDataError

logger = logging.getLogger(__name__)


def load_from_json(json_str, session=None, return_on_error=True, n_tries=1):
    try:
        irdata = IRData.from_json(json_str, fill_cache=True)
    except IRDataError as err:
        if return_on_error:
            logger.info('error creating irdata: %s', err)
            return
        else:
            raise err

    session = session or Session()

    # Try to load models from irdata "n_tries" times
    for i in range(n_tries):
        try:
            load_models_from_irdata(irdata, session)
        except exc.DBAPIError as err:
            if err.connection_invalidated:
                logger.error('caught a disconnect, try #%s, err=%s', i, err)
                time.sleep(10)
                session.rollback()
                continue
            else:
                raise
        else:
            # load to db was successful!
            break
        finally:
            session.close()
    else:
        # models were not loaded in "n_tries" times
        logger.error('giving up!')
        raise Exception('unable to load models from irdata')


def load_models_from_irdata(irdata, session=None):
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

    molecule = tables.Molecule(
        molecule_hash=irdata.molecule_hash,
        score=irdata.score,
    )

    history = tables.History(
        history_hash=irdata.history_hash,
        total_moves=irdata.total_moves,
    )

    puzzle = tables.Puzzle(puzzle_id=irdata.puzzle_id)

    team = tables.Team(
        team_name=irdata.team_name,
        team_type=irdata.team_type,
    )

    session.add(pdb_file)
    session.add(molecule)
    session.add(history)
    puzzle = session.merge(puzzle)
    team = session.merge(team)
    session.commit()

    competition = tables.Competition(
        team_id=team.team_id,
        puzzle_id=puzzle.puzzle_id,
    )

    solution = tables.Solution(
        molecule_id=molecule.molecule_id,
        history_id=history.history_id,
    )


    session.add(solution)
    competition = session.merge(competition)
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

    edit_n = 0
    prev_molecule = None
    for edit_data in irdata.edits:
        molecule = tables.Molecule(molecule_hash=edit_data.molecule_hash)
        molecule = session.merge(molecule)
        session.commit()

        if prev_molecule is not None:
            edit_n += 1
            edit = tables.Edit(
                history_id=history.history_id,
                molecule_id=molecule.molecule_id,
                prev_molecule_id=prev_molecule.molecule_id,
                moves=edit_data.moves,
                edit_n=edit_n
            )
            session.add(edit)

        prev_molecule = molecule
    else:
        session.commit()

    # Record player actions for top solutions only
    if irdata.solution_type == 'top':
        for player_data in irdata.player_pdls:
            # Get or create player
            player = tables.Player(player_name=player_data.player_name,
                                   team_id=team.team_id)
            player = session.merge(player)
            session.commit()

            # Record player actions
            for action_name, action_n in player_data.actions.items():
                # Get or create action
                action = tables.Action(action_name=action_name)
                action = session.merge(action)
                session.commit()

                player_action = tables.PlayerActions(
                    player_id=player.player_id,
                    action_id=action.action_id,
                    action_n=action_n,
                )
                session.add(player_action)
            else:
                session.commit()
