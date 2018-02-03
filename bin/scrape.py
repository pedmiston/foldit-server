#!/usr/bin/env python
"""scrape.py scrapes solution files and stores them in the cloud."""
import sys
import subprocess
import time
from pathlib import Path

repo_dir = Path(__file__).absolute().parent.parent
workload_dir = Path(repo_dir, 'playbooks/data/workload')
batches_per_push = 100
cmdf = 'ansible-playbook {name}.yml {arg_string}'
errorf = 'error in playbook: {cmd}\n{stdout}\n'

def run(name, arg_string='', ignore_errors=False):
    t = time.strftime('%H:%M:%S', time.localtime())
    print('[{}] running playbook: {} {}'.format(t, name, arg_string),
          flush=True)
    cmd = cmdf.format(name=name, arg_string=arg_string)
    try:
        subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        if ignore_errors:
            # convert bytes to string so that new lines are printed
            output_str = err.output.decode('utf-8')
            sys.stderr.write(errorf.format(cmd=err.cmd, stdout=output_str))
        else:
            raise err

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--retry', action='store_true')
    args = parser.parse_args()

    if not args.retry:
        run('prepare')
        run('find')
        run('workload')
        run('install')

    for i, workload in enumerate(workload_dir.iterdir()):
        # Skip files that have a file extension
        if workload.suffix != '':
            continue
        run('scrape', arg_string='-e workload={}'.format(workload.name))
        if i%batches_per_push == batches_per_push-1:
            run('push')

    run('push', ignore_errors=True)
    run('cleanup')
