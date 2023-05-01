import os

from kubernetes import client, config
from kubernetes.client import ApiClient

NAMESPACE = os.environ.get('NAMESPACE', 'cykube')

k8clients = dict()


def init():
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        # we're inside a cluster
        config.load_incluster_config()
    else:
        # we're not
        config.load_kube_config()
    api = k8clients['api'] = ApiClient()
    k8clients['batch'] = client.BatchV1Api(api)
    k8clients['event'] = client.EventsV1Api(api)
    k8clients['core'] = client.CoreV1Api(api)
    k8clients['custom'] = client.CustomObjectsApi(api)


def get_batch_api() -> client.BatchV1Api:
    return k8clients['batch']


def get_events_api() -> client.EventsV1Api:
    return k8clients['event']


def get_core_api() -> client.CoreV1Api:
    return k8clients['core']


def get_custom_api() -> client.CustomObjectsApi:
    return k8clients['custom']
