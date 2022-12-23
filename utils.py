import datetime
import os
import subprocess
from decimal import Decimal
from json import JSONEncoder
from sys import stdout
from uuid import UUID

from .enums import TestRunStatus

FAILED_STATES = [TestRunStatus.timeout, TestRunStatus.failed]


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


class MaxBodySizeException(Exception):
    def __init__(self, body_len: str):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)
