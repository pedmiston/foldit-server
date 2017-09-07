#!/usr/bin/env bash
source ~/.profile
~/foldit/playbooks/scripts/select-new-puzzle.py ~/foldit/playbooks/puzzle-info.csv > new-puzzle-id && \
puzzle_id=`cat new-puzzle-id` && \
ansible-playbook ~/foldit/playbooks/get_solutions.yml -e puzzle_id=${puzzle_id}
