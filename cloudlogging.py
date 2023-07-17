from __future__ import annotations

import traceback

import google.cloud.logging
import httpx
from loguru import logger


class StackDriverSink:
    def __init__(self, logger_name='cykube'):
        self.logging_client = google.cloud.logging.Client()
        self.logger = self.logging_client.logger(logger_name)
        with open('/etc/hostname') as f:
            self.hostname = f.read().strip()

    def write(self, message):
        """
        Loguru stackdriver logging
        source: https://github.com/Delgan/loguru/blob/master/loguru/_handler.py
        """
        record = message.record

        if 'kube-probe' in record["message"]:
            return
        log_info = {
            "exception": (None if record["exception"] is None
                          else ''.join(traceback.format_exception(None,
                                                                  record["exception"].value,
                                                                  record["exception"].traceback))),
            "message": record["message"],
            "module": record["module"],
            "name": record["name"],
            "pod": self.hostname
        }
        if 'extra' in record:
            for k, v in record["extra"].items():
                log_info[k] = v

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
            resp = httpx.get('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email',
                             headers={'Metadata-Flavor': 'Google'})
            if resp.status_code == 200 and resp.text.endswith('gserviceaccount.com'):
                logger.add(StackDriverSink(name))
                client = google.cloud.logging.Client()
                client.setup_logging()
    except:
        pass
