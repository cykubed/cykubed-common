from __future__ import annotations

import traceback

import google.cloud.logging
import httpx
from loguru import logger


class StackDriverSink:
    def __init__(self, logger_name='cykube'):
        self.logging_client = google.cloud.logging.Client()
        self.logger = self.logging_client.logger(logger_name)

    def write(self, message):
        '''
        source: https://github.com/Delgan/loguru/blob/master/loguru/_handler.py
        '''
        record = message.record
        log_info = {
            "elapsed": {
                "microseconds": record["elapsed"] // record["elapsed"].resolution,
                "seconds": record["elapsed"].total_seconds(),
            },
            "exception": (None if record["exception"] is None
                          else ''.join(traceback.format_exception(None,
                                                                  record["exception"].value,
                                                                  record["exception"].traceback))),
            "message": record["message"],
            "module": record["module"],
            "name": record["name"],
            "process": {"id": record["process"].id, "name": record["process"].name},
            "thread": {"id": record["thread"].id, "name": record["thread"].name},
            "extra": {k: str(v)
                      for k, v in record["extra"].items()
                      if 'record' not in record["extra"]}
        }
        self.logger.log_struct(log_info,
                               severity=record['level'].name,
                               source_location={'file': record['file'].name,
                                                'function': record["function"],
                                                'line': record["line"]})


def configure_stackdriver_logging(name: str):
    # if we're running in GCP, use structured logging
    try:
        resp = httpx.get('http://metadata.google.internal')
        if resp.status_code == 200 and resp.headers['metadata-flavor'] == 'Google':
            logger.add(StackDriverSink(name))
    except:
        pass
