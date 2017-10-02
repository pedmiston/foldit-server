#!/usr/bin/env python
"""scrape.py scrapes solution files and stores them in the cloud."""
import sys
import subprocess
import time
from pathlib import Path

cmdf = 'ansible-playbook {name}.yml {arg_string}'
errorf = 'error in playbook: {cmd}\n{stdout}\n'

def run(name, arg_string=''):
    print('running playbook: {} {}'.format(name, arg_string), flush=True)
    cmd = cmdf.format(name=name, arg_string=arg_string)
    try:
        subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        # convert bytes to string so that new lines are printed
        output_str = err.output.decode('utf-8')
        sys.stderr.write(errorf.format(cmd=err.cmd, stdout=output_str))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--workload-dir', default='data/workload')
    parser.add_argument('-s', '--batches-per-push', type=int, default=100)
    parser.add_argument('--skip-find', action='store_true')
    parser.add_argument('--dont-update-scraper', action='store_true')
    args = parser.parse_args()

    run('prepare')

    # Find available solutions unless told not to
    if not args.skip_find:
        run('find')
        run('workload')

    # Install/update scraper unless told not to
    if not args.dont_update_scraper:
        run('install')

    workload_dir = Path(args.workload_dir)
    for i, workload in enumerate(workload_dir.iterdir()):
        # Skip files that have a file extension
        if workload.suffix != '':
            continue
        run('scrape', arg_string='-e workload={}'.format(workload.name))
        if i%args.batches_per_push == args.batches_per_push-1:
            run('push')

    run('push')
    run('cleanup')
