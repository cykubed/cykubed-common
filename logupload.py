import tempfile
import threading
import time
import traceback

import httpx
from loguru import logger

from common.utils import get_headers
from settings import settings

logfile = None
logthread: threading.Thread = None
running = True


def upload_exception_trace(trid: id):
    upload_logs(trid, traceback.format_exc().encode('utf8'))


def upload_log_line(trid: id, line: str):
    logger.info(line)
    upload_logs(trid, (line+"\n").encode('utf8'))


def upload_logs(trid: int, data):
    r = httpx.post(f'{settings.MAIN_API_URL}/agent/testrun/{trid}/logs',
                   data=data, headers=get_headers())
    if r.status_code != 200:
        logger.error(f"Failed to push logs")


def log_watcher(trid: int, fname: str):
    global running
    with open(fname, 'rb') as logfile:
        while running:
            logs = logfile.read()
            if logs:
                upload_logs(trid, logs)
            time.sleep(settings.LOG_UPDATE_PERIOD)


def start_log_thread(testrun_id: int):
    global logfile
    global logthread
    logfile = tempfile.NamedTemporaryFile(suffix='.log', mode='w')
    logthread = threading.Thread(target=log_watcher, args=(testrun_id, logfile.name))
    logthread.start()
    return logfile


def stop_log_thread():
    global running
    global logthread
    running = False
    logthread.join()
