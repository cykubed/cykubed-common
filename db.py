import os
from functools import cache
from time import sleep

import dns
from loguru import logger
from redis import Redis
from redis.asyncio.retry import Retry as AsyncRetry
from redis.asyncio.sentinel import Sentinel as AsyncSentinel
from redis.backoff import ConstantBackoff
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    TimeoutError
)
from redis.retry import Retry as SyncRetry
from redis.sentinel import Sentinel as SyncSentinel

from common.enums import TestRunStatus, AgentEventType
from common.schemas import AgentCompletedBuildMessage, NewTestRun, AgentStatusChanged
from common.settings import settings


@cache
def async_redis():
    return get_redis(AsyncSentinel, AsyncRetry)


@cache
def sync_redis():
    return get_redis(SyncSentinel, SyncRetry)


def get_redis(sentinel_class, retry_class):
    if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/namespace'):
        # we're running inside K8
        hosts = get_redis_sentinel_hosts()
        while len(hosts) < 3:
            logger.info(f'Can only see {len(hosts)} Redis hosts - waiting...')
            sleep(5)
            hosts = get_redis_sentinel_hosts()

        sentinel = sentinel_class(hosts, sentinel_kwargs=dict(password=os.environ['REDIS_PASSWORD'],
                                                        decode_responses=True))
        retry = retry_class(ConstantBackoff(2), 5)
        return sentinel.master_for("mymaster", password=os.environ['REDIS_PASSWORD'], retry=retry,
                                   decode_responses=True,
                                    retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])
    else:
        return Redis(os.environ.get('REDIS_HOST', 'localhost'))


def send_status_message(testrun_id: int, status: TestRunStatus):
    sync_redis().publish('messages', AgentStatusChanged(testrun_id=testrun_id,
                                                        type=AgentEventType.status,
                                                        status=status).json())


async def new_testrun(tr: NewTestRun):
    await async_redis().set(f'testrun:{tr.id}', tr.json())


async def get_testrun(id: int) -> NewTestRun | None:
    d = await async_redis().get(f'testrun:{id}')
    if d:
        return NewTestRun.parse_raw(d['data'])
    return None


async def set_build_details(testrun: NewTestRun, specs: list[str]) -> NewTestRun | None:
    r = async_redis()
    await r.sadd(f'testrun:{testrun.id}:specs', *specs)
    testrun.status = TestRunStatus.running
    await r.set(f'testrun:{testrun.id}', testrun.json())
    await async_redis().publish('messages', AgentCompletedBuildMessage(sha=testrun.sha, specs=specs))


def get_redis_sentinel_hosts():
    return list(set([(x.target.to_text(), 26379) for x in
              dns.resolver.resolve(f'redis-headless.{settings.NAMESPACE}.svc.cluster.local', 'SRV')]))
