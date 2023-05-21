import os
from functools import cache
from time import sleep

import dns.resolver
from loguru import logger
from pydantic import BaseSettings
from redis import Sentinel as SyncSentinel, Redis as SyncRedis, BusyLoadingError, ConnectionError, TimeoutError
from redis.asyncio import Sentinel as AsyncSentinel, Redis as AsyncRedis
from redis.asyncio.retry import Retry as AsyncRetry
from redis.backoff import ConstantBackoff
from redis.retry import Retry as SyncRetry


class RedisSettings(BaseSettings):
    K8: bool = True
    REDIS_HOST = 'localhost'
    REDIS_DB: int = 0
    REDIS_NODES: int = 3
    REDIS_PASSWORD = ''
    REDIS_PORT = 6379
    REDIS_SENTINEL_PREFIX: str = ''
    NAMESPACE = 'cykubed'

    def get_redis_sentinel_hosts(self):
        return list(set([(x.target.to_text(), 26379) for x in
                         dns.resolver.resolve(
                             f'{self.REDIS_SENTINEL_PREFIX}.{self.NAMESPACE}.svc.cluster.local', 'SRV')]))


@cache
def sync_redis() -> SyncRedis:
    return get_redis(SyncSentinel, SyncRedis, SyncRetry)


_async_redis = None


def get_cached_async_redis() -> AsyncRedis:
    global _async_redis
    if not _async_redis:
        _async_redis = get_redis(AsyncSentinel, AsyncRedis, AsyncRetry)
    return _async_redis


def async_redis() -> AsyncRedis:
    """
    Indirection to make this easier to mock
    """
    return get_cached_async_redis()


def ping_redis() -> bool:
    try:
        if sync_redis().ping():
            return True
        return False
    except ConnectionError:
        return False


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
    if redis_class:
        retry = retry_class(ConstantBackoff(2), 5)
    else:
        retry = None

    settings = RedisSettings()

    if settings.K8 and os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/namespace') \
            and settings.REDIS_NODES > 1:
        logger.info('Assuming replicated Redis with Sentinel')
        # we're running inside K8
        hosts = []
        while len(hosts) < settings.REDIS_NODES:
            try:
                hosts = settings.get_redis_sentinel_hosts()
                if len(hosts) == settings.REDIS_NODES:
                    break
                logger.info(f'Can only see {len(hosts)} Redis hosts - waiting...')
                sleep(30)
            except:
                logger.info(f'No Redis hosts visible - waiting...')
                sleep(30)
                hosts = []

        retry = retry_class(ConstantBackoff(10), 30)
        sentinel = sentinel_class(hosts, sentinel_kwargs=dict(password=settings.REDIS_PASSWORD,
                                                              db=settings.REDIS_DB,
                                                              retry=retry,
                                                              retry_on_error=[BusyLoadingError, ConnectionError,
                                                                              TimeoutError],
                                                              decode_responses=True))
        return sentinel.master_for("mymaster", password=settings.REDIS_PASSWORD, retry=retry,
                                   decode_responses=True, db=settings.REDIS_DB,
                                   retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])
    else:
        logger.info('Assuming standalone Redis')
        return redis_class(host=settings.REDIS_HOST, db=settings.REDIS_DB,
                           password=settings.REDIS_PASSWORD,
                           decode_responses=True,
                           port=settings.REDIS_PORT,
                           retry=retry, retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])


def get_specfile_log_key(trid: int, file: str):
    return f'testrun:{trid}:spec:{file}:logs'
