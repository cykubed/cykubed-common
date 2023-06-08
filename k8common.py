import os

from kubernetes_asyncio import client, config
from kubernetes_asyncio.client import ApiClient
from loguru import logger

NAMESPACE = os.environ.get('NAMESPACE', 'cykube')

k8clients = dict()


async def init():
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        # we're inside a cluster
        config.load_incluster_config()
    else:
        # we're not
        await config.load_kube_config()
    api = k8clients['api'] = ApiClient()
    k8clients['batch'] = client.BatchV1Api(api)
    k8clients['event'] = client.EventsV1Api(api)
    k8clients['core'] = client.CoreV1Api(api)
    k8clients['custom'] = client.CustomObjectsApi(api)


async def close():
    try:
        await get_client().close()
    except Exception as ex:
        logger.error('Faield to close K8 client')


def get_client() -> ApiClient:
    return k8clients['api']


def get_batch_api() -> client.BatchV1Api:
    return k8clients['batch']


def get_events_api() -> client.EventsV1Api:
    return k8clients['event']


def get_core_api() -> client.CoreV1Api:
    return k8clients['core']


def get_custom_api() -> client.CustomObjectsApi:
    return k8clients['custom']
