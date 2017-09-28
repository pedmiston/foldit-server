#!/usr/bin/env python
# list-solution-filenames.py lists the solution filenames within a json file.
# Usage: list-solution-filenames [JSON_DATA_FILE]
import sys
import json
from pathlib import Path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('json')
    args = parser.parse_args()
    filename = Path(args.json)
    assert filename.exists(), "json file doesn't exist"

    with filename.open() as f:
      for j in f:
          try:
              d = json.loads(j)
              s = d['FILEPATH']
          except Exception as e:
              sys.stderr.write("error extracting FILEPATH: "+e)
          else:
              sys.stdout.write(s+'\n')
