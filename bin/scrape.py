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

def parse_args():
    assert len(sys.argv) == 3, 'incorrect number of arguments\n' + usage
    workload_dir = Path(sys.argv[1])
    assert workload_dir.is_dir(), 'workload dir does not exist\n' + usage
    try:
      batches_per_push = int(sys.argv[2])
    except Exception as e:
      raise AssertionError('invalid batches_per_push: {}\n{}'.format(e, usage))
    return workload_dir, batches_per_push

def run(cmd):
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        sys.stderr.write(error.format(cmd=err.cmd, stdout=str(err.output)))

if __name__ == '__main__':
    run(find)
    workload_dir, batches_per_push = parse_args()
    for i, workload in enumerate(workload_dir.iterdir()):
        print('{}: {}'.format(i, workload))
        run(scrape.format(workload.name))
        if i%batches_per_push == batches_per_push-1:
            print('pushing...')
            run(push)

    subprocess.call('rm data/available/*.txt data/remaining/*.txt')
