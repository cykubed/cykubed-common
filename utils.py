import datetime
import os
import subprocess
from decimal import Decimal
from json import JSONEncoder
from sys import stdout
from uuid import UUID


def runcmd(cmd: str, logfile=None, **kwargs):
    if not logfile:
        logfile = stdout
    logfile.write(cmd+'\n')
    env = os.environ.copy()
    env['PATH'] = './node_modules/.bin:' + env['PATH']
    subprocess.check_call(cmd, shell=True, stderr=logfile, stdout=logfile, env=env, **kwargs)


# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, UUID) or isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)
