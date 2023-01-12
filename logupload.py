from functools import lru_cache

import httpx
from loguru import logger

from common import schemas
from common.utils import get_headers
from settings import settings


def upload_logs(project_id: int, local_id: int, data):
    r = httpx.post(f'{settings.MAIN_API_URL}/agent/testrun/{project_id}/{local_id}/logs',
                   data=data, headers=get_headers())
    if r.status_code != 200:
        logger.error(f"Failed to push logs")


def post_testrun_status(tr: schemas.NewTestRun, status: str):
    post_status(tr.project.id, tr.local_id, status)


@lru_cache(maxsize=10000)
def post_status(project_id: int, local_id: int, status: str):
    resp = httpx.put(f'{settings.MAIN_API_URL}/agent/testrun/{project_id}/{local_id}/status/{status}',
                     headers=get_headers())
    if resp.status_code != 200:
        raise Exception(f"Failed to update status for run {local_id} on project {project_id}")
