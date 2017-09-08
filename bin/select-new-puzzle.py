#!/usr/bin/env python
import sys
import unipath
import pandas

if __name__ == '__main__':
    assert len(sys.argv) == 2 and unipath.Path(sys.argv[1]).exists()
    available_puzzles = (pandas.read_csv(sys.argv[1])
                               .dropna(how='all', subset=['top', 'all']))
    
    data_dir = unipath.Path('/home/pierce/foldit/playbooks/data-raw/').absolute()
    assert data_dir.isdir()
    puzzles_already_downloaded = [int(p.name.split('-')[1])
        for p in data_dir.listdir('puzzle-*')]
    
    remaining_puzzles = available_puzzles.ix[
        ~available_puzzles.id.isin(puzzles_already_downloaded)
    ]

    if len(remaining_puzzles) == 0:
        sys.exit('no puzzles remaining')
    sys.stdout.write(str(remaining_puzzles.id.iloc[0]))
