import os
from functools import cache
from time import sleep

import dns.resolver
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
    AgentSpecCompleted, SpecResult, AgentRunnerStopped, AgentBuildStarted
from common.settings import settings
from common.utils import utcnow


@cache
def get_sync_redis():
    return get_redis(SyncSentinel, SyncRedis, SyncRetry)


@cache
def get_async_redis():
    return get_redis(AsyncSentinel, AsyncRedis, AsyncRetry)

#
# Odd bit of redirection is purely to make mocking easier
#


def sync_redis() -> SyncRedis:
    return get_sync_redis()


def async_redis() -> AsyncRedis:
    return get_async_redis()


def get_redis(sentinel_class, redis_class, retry_class=None):
    """
    We use Redis as the glue as the central "database", and the glue that binds runners to agents via the
    "messages" queue. On a clean install it's Redis we're waiting for as it takes a while to spin up the
    nodes, so we don't start until we can contact all of them.

    The choice of a distributed Redis is because the K8 cluster may decide to move nodes around, particularly
    when scaling up for a large parallel Job. While we _could_ get away with a single Redis standalone deploy,
    test runs could potentially block for a long time while the node is moved around.

    :param sentinel_class:
    :param redis_class:
    :param retry_class:
    """
    if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/namespace'):
        # we're running inside K8
        hosts = []
        while len(hosts) < settings.REDIS_NODES:
            try:
                hosts = get_redis_sentinel_hosts()
                if len(hosts) == settings.REDIS_NODES:
                    break
                logger.info(f'Can only see {len(hosts)} Redis hosts - waiting...')
                sleep(5)
            except:
                logger.info(f'No Redis hosts visible - waiting...')
                sleep(5)
                hosts = []

        sentinel = sentinel_class(hosts, sentinel_kwargs=dict(password=settings.REDIS_PASSWORD,
                                                              db=settings.REDIS_DB,
                                                              decode_responses=True))
        retry = retry_class(ConstantBackoff(2), 5)
        return sentinel.master_for("mymaster", password=settings.REDIS_PASSWORD, retry=retry,
                                   decode_responses=True, db=settings.REDIS_DB,
                                    retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])
    else:
        return redis_class(host=settings.REDIS_HOST, db=settings.REDIS_DB, decode_responses=True)


async def send_runner_stopped_message(testrun_id: int, duration, terminated=False):
    """
    Send the runner stopped message
    :param testrun_id:
    :param duration:
    :param terminated:
    :return:
    """
    await send_message(AgentRunnerStopped(testrun_id=testrun_id,
                                          type=AgentEventType.runner_stopped,
                                          duration=duration,
                                          terminated=terminated))


async def send_status_message(testrun_id: int, status: TestRunStatus):
    """
    Send the "status changed" message
    :param testrun_id:
    :param status:
    :return:
    """
    await send_message(AgentStatusChanged(testrun_id=testrun_id,
                                          type=AgentEventType.status,
                                          status=status))


async def new_testrun(tr: NewTestRun):
    await async_redis().set(f'testrun:{tr.id}', tr.json())


async def get_testrun(id: int) -> NewTestRun | None:
    d = await async_redis().get(f'testrun:{id}')
    if d:
        return NewTestRun.parse_raw(d)
    return None


async def send_message(msg):
    await async_redis().rpush('messages', msg.json())


def send_message_sync(msg):
    sync_redis().rpush('messages', msg.json())


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
    """
    Fetch the next spec
    :param trid:
    :param hostname:
    :return:
    """
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


async def send_build_started_message(trid: int):
    await send_message(AgentBuildStarted(type=AgentEventType.build_started,
                                         testrun_id=trid,
                                         started=utcnow()))


async def set_build_details(testrun: NewTestRun, specs: list[str]) -> NewTestRun | None:
    r = async_redis()
    await r.sadd(f'testrun:{testrun.id}:specs', *specs)
    testrun.status = TestRunStatus.running
    await r.set(f'testrun:{testrun.id}', testrun.json())
    await send_message(AgentCompletedBuildMessage(type=AgentEventType.build_completed,
                                                  testrun_id=testrun.id,
                                                  finished=utcnow(),
                                                  sha=testrun.sha, specs=specs))
    await send_message(AgentStatusChanged(testrun_id=testrun.id,
                       type=AgentEventType.status,
                       status=TestRunStatus.running))


def get_redis_sentinel_hosts():
    return list(set([(x.target.to_text(), 26379) for x in
              dns.resolver.resolve(f'cykube-redis-headless.{settings.NAMESPACE}.svc.cluster.local', 'SRV')]))
