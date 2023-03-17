import os
from functools import cache
from time import sleep

import dns
from loguru import logger
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
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
from common.schemas import AgentCompletedBuildMessage, NewTestRun, AgentStatusChanged, AgentSpecStarted, \
    AgentSpecCompleted, SpecResult
from common.settings import settings
from common.utils import utcnow


@cache
def sync_redis() -> SyncRedis:
    return get_redis(SyncSentinel, SyncRedis, SyncRetry)


@cache
def async_redis() -> AsyncRedis:
    return get_redis(AsyncSentinel, AsyncRedis, AsyncRetry)


def get_redis(sentinel_class, redis_class, retry_class):
    if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/namespace'):
        # we're running inside K8
        hosts = get_redis_sentinel_hosts()
        while len(hosts) < 3:
            logger.info(f'Can only see {len(hosts)} Redis hosts - waiting...')
            sleep(5)
            hosts = get_redis_sentinel_hosts()

        sentinel = sentinel_class(hosts, sentinel_kwargs=dict(password=settings.REDIS_PASSWORD,
                                                              decode_responses=True))
        retry = retry_class(ConstantBackoff(2), 5)
        return sentinel.master_for("mymaster", password=settings.REDIS_PASSWORD, retry=retry,
                                   decode_responses=True,
                                    retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])
    else:
        return redis_class(host=settings.REDIS_HOST, decode_responses=True)


async def send_status_message(testrun_id: int, status: TestRunStatus):
    await async_redis().publish('messages', AgentStatusChanged(testrun_id=testrun_id,
                                                               type=AgentEventType.status,
                                                               status=status).json())


async def new_testrun(tr: NewTestRun):
    await async_redis().set(f'testrun:{tr.id}', tr.json())


async def get_testrun(id: int) -> NewTestRun | None:
    d = await async_redis().get(f'testrun:{id}')
    if d:
        return NewTestRun.parse_raw(d)
    return None


async def send_message(msg):
    await async_redis().publish('messages', msg.json())


def send_message_sync(msg):
    sync_redis().publish('messages', msg.json())


async def cancel_testrun(trid: int):
    """
    Just remove the keys
    :param trid: test run ID
    """
    r = async_redis()
    await r.delete(f'testrun:{trid}:specs')
    await r.delete(f'testrun:{trid}')


def spec_terminated(trid: int, spec: str):
    """
    Return the spec to the pool
    """
    sync_redis().sadd(f'testrun:{trid}:specs', spec)


async def next_spec(trid: int, hostname: str) -> str | None:
    spec = await async_redis().spop(f'testrun:{trid}:specs')
    if spec:
        await send_message(AgentSpecStarted(type=AgentEventType.spec_started,
                                            testrun_id=trid,
                                            file=spec,
                                            started=utcnow(),
                                            pod_name=hostname))
    return spec


async def send_spec_completed_message(tr: NewTestRun, spec: str, result: SpecResult):
    await send_message(AgentSpecCompleted(type=AgentEventType.spec_completed,
                                          result=result,
                                          testrun_id=tr.id,
                                          file=spec,
                                          finished=utcnow()))


async def set_build_details(testrun: NewTestRun, specs: list[str]) -> NewTestRun | None:
    r = async_redis()
    await r.sadd(f'testrun:{testrun.id}:specs', *specs)
    testrun.status = TestRunStatus.running
    await r.set(f'testrun:{testrun.id}', testrun.json())
    await send_message(AgentCompletedBuildMessage(type=AgentEventType.build_completed,
                                                  testrun_id=testrun.id,
                                                  sha=testrun.sha, specs=specs))
    await send_message(AgentStatusChanged(testrun_id=testrun.id,
                       type=AgentEventType.status,
                       status=TestRunStatus.running))


def get_redis_sentinel_hosts():
    return list(set([(x.target.to_text(), 26379) for x in
              dns.resolver.resolve(f'redis-headless.{settings.NAMESPACE}.svc.cluster.local', 'SRV')]))
