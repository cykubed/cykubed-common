import traceback

import httpx
from loguru import logger

from common.utils import get_headers
from settings import settings

logfile = None
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


def post_status(testrun_id: int, status: str):
    resp = httpx.put(f'{settings.MAIN_API_URL}/agent/testrun/{testrun_id}/status/{status}', headers=get_headers())
    if resp.status_code != 200:
        raise Exception(f"Failed to update status for run {testrun_id}")
