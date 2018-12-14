import subprocess
import json
import os
import sys

# if running in lambda


def runit(event, context):
    # process = subprocess.run(['./halite', '--width', '32', '--height', '32',
    #                           'python3 run.py', 'python3 run.py'],
    #                          capture_output=True)

    process = subprocess.run(['python3', 'run.py'],
                             capture_output=True)
    # print(process)
    return json.dumps({'result': process.stdout.decode(), 'err': process.stderr.decode()})


if __name__ == '__main__':
    print(runit('', ''))
