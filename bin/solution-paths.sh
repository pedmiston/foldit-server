#!/usr/bin/env bash
# Find all available solution pdb files for a given puzzle id
PUZZLE_ID=$1
find ~/fetch/solution_${PUZZLE_ID}/ -maxdepth 1 -type d \
  -name "top" -exec find {} -name "*.pdb" \; \
  -o -name "all" -exec find {} -name "*.pdb" \;
