#!/usr/bin/env python
import sys
import glob
import json
import pandas
import unipath
import foldit


if __name__ == '__main__':
    assert len(sys.argv) == 2 and unipath.Path(sys.argv[1]).exists()
    available_solutions = pandas.read_table(sys.argv[1], names=['path']).path
    # TODO: Figure out how to merge sqlite db
    solutions_not_downloaded = available_solutions
    solutions_not_downloaded.to_csv(sys.stdout, index=False)
