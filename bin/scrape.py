#!/usr/bin/env python
import sys
import subprocess
import time
from pathlib import Path

usage = 'scrape [workload_dir] [workloads_per_push]'

# Ansible playbook commands
find = 'ansible-playbook find.yml'
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
    parser.add_argument('-w', '--workload', default='data/workload')
    parser.add_argument('-s', '--batches-per-push', type=int, default=100)
    parser.add_argument('--skip-find', action='store_true')
    args = parser.parse_args()

    if args.skip_find:
        run(find)

    for i, workload in enumerate(args.workload_dir.iterdir()):
        print('{}: {}'.format(i, workload))
        run(scrape.format(workload.name))
        if i%args.batches_per_push == args.batches_per_push-1:
            print('pushing...')
            run(push)

    subprocess.call('rm data/available/*.txt data/remaining/*.txt')
