#!/usr/bin/env python
# list-solution-filenames.py lists the solution filenames within a json file.
# Usage: list-solution-filenames [JSON_DATA_FILE]
import sys
import json
from os import path

assert len(sys.argv) == 2, "must provide json file"
assert path.exists(sys.argv[1]), "json file doesn't exist"

for j in open(sys.argv[1], 'r'):
    try:
        d = json.loads(j)
        f = d['FILEPATH'][0]
    except Exception as e:
        sys.stderr.write("error extracting FILEPATH: "+e)
    else:
        sys.stdout.write(f+'\n')
