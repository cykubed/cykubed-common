import base64
import datetime
import logging
import os
import time
from decimal import Decimal
from functools import cache
from json import JSONEncoder
from time import sleep
from uuid import UUID

from loguru import logger
from pymongo import MongoClient

from . import schemas
from .enums import TestRunStatus
from .exceptions import MongoConnectionException
from .settings import settings

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


def encode_testrun(tr: schemas.NewTestRun) -> str:
    return base64.b64encode(tr.json().encode()).decode()


def decode_testrun(payload: str) -> schemas.NewTestRun:
    return schemas.NewTestRun.parse_raw(base64.b64decode(payload).decode())


def get_headers():
    token = os.environ.get('API_TOKEN')
    return {'Authorization': f'Bearer {token}',
            'Accept': 'application/json'}


def disable_hc_logging():
    class HCFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.getMessage().find("GET /hc") == -1

    # disable logging for health check
    logging.getLogger("uvicorn.access").addFilter(HCFilter())


def utcnow():
    return datetime.datetime.utcnow()


def ensure_mongo_connection():
    cl = mongo_sync_client()
    if settings.MONGO_ROOT_PASSWORD:
        start = time.time()
        num_nodes = len(cl.nodes)
        while num_nodes < 3:
            logger.info(f"Only {num_nodes} available: waiting...")
            t = time.time() - start
            if t > settings.MONGO_CONNECT_TIMEOUT:
                raise MongoConnectionException()
            sleep(10)
            num_nodes = len(cl.nodes)

            logger.info(f"Connected to MongoDB replicaset")


@cache
def mongo_sync_client():
    if settings.MONGO_ROOT_PASSWORD:
        return MongoClient(host=settings.MONGO_HOST,
                           username=settings.MONGO_USER,
                           password=settings.MONGO_ROOT_PASSWORD)
    return MongoClient()
