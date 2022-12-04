import os
import subprocess
from sys import stdout


def runcmd(cmd: str, logfile=None, **kwargs):
    if not logfile:
        logfile = stdout
    logfile.write(cmd+'\n')
    env = os.environ.copy()
    env['PATH'] = './node_modules/.bin:' + env['PATH']
    subprocess.check_call(cmd, shell=True, stderr=logfile, stdout=logfile, env=env, **kwargs)
