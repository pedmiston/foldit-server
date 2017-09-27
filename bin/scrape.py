#!/usr/bin/env python
"""scrape.py scrapes solution files and stores them in the cloud."""
import sys
import subprocess
import time
from pathlib import Path

# Ansible playbook commands
find = 'ansible-playbook find.yml'
install = 'ansible-playbook install.yml'
scrape = 'ansible-playbook scrape.yml -e workload={}'
push = 'ansible-playbook push.yml'

error = 'error in playbook: {cmd}\n{stdout}\n'

def run(cmd):
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        sys.stderr.write(error.format(cmd=err.cmd, stdout=str(err.output)))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--workload-dir', default='data/workload')
    parser.add_argument('-s', '--batches-per-push', type=int, default=100)
    parser.add_argument('--skip-find', action='store_true')
    parser.add_argument('--dont-update-scraper', action='store_true')
    args = parser.parse_args()

    # Find available solutions unless told not to
    if not args.skip_find:
        print('running find.yml playbook...', flush=True)
        run(find)

    # Install/update scraper unless told not to
    if not args.dont_update_scraper:
        run(install)

    workload_dir = Path(args.workload_dir)
    for i, workload in enumerate(workload_dir.iterdir()):
        # Skip any file in the workload dir that has a file extension
        if workload.suffix != '':
            continue

        print('{}: {}'.format(i, workload), flush=True)
        run(scrape.format(workload.name))

        if i%args.batches_per_push == args.batches_per_push-1:
            print('pushing...', flush=True)
            run(push)

    subprocess.call('rm data/available/*.txt data/remaining/*.txt')
