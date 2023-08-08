import datetime
import hashlib
import logging
import os
from decimal import Decimal
from json import JSONEncoder
from uuid import UUID

from .enums import TestRunStatus
from .exceptions import BuildFailedException

FAILED_STATES = [TestRunStatus.timeout, TestRunStatus.failed]
ACTIVE_STATES = [TestRunStatus.started, TestRunStatus.running]


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


def get_headers():
    token = os.environ.get('API_TOKEN')
    return {'Authorization': f'Bearer {token}',
            'Accept': 'application/json'}


def disable_hc_logging():
    class HCFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            msg = record.getMessage()
            return msg.find("GET / ") == -1 and record.getMessage().find("kube-probe") == -1

    # disable logging for health check
    logging.getLogger("uvicorn.access").addFilter(HCFilter())


def utcnow():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_hostname():
    with open('/etc/hostname') as f:
        return f.read().strip()


def get_lock_hash(build_dir):
    m = hashlib.sha256()
    lockfile = os.path.join(build_dir, 'package-lock.json')
    if not os.path.exists(lockfile):
        lockfile = os.path.join(build_dir, 'yarn.lock')

    if not os.path.exists(lockfile):
        raise BuildFailedException("No lock file")

    # hash the lock
    with open(lockfile, 'rb') as f:
        m.update(f.read())
    return m.hexdigest()
