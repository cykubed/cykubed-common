from functools import cache
from time import sleep

from loguru import logger
from pymongo import MongoClient

from common.settings import settings


@cache
def sync_client():
    if settings.TEST:
        from mongomock import MongoClient as MockClient
        return MockClient()
    if settings.MONGO_ROOT_PASSWORD:
        return MongoClient(host=settings.MONGO_HOST,
                           username=settings.MONGO_USER,
                           password=settings.MONGO_ROOT_PASSWORD)
    return MongoClient()


def ensure_connection():
    if settings.MONGO_ROOT_PASSWORD:
        # we're running in a cluster: wait till we can see 3 nodes
        cl = sync_client()
        num_nodes = len(cl.nodes)
        while num_nodes < 3:
            logger.info(f"Only {num_nodes} available: waiting...")
            sleep(10)
            num_nodes = len(cl.nodes)

        logger.info(f"Connected to MongoDB replicaset")
