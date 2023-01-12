import os
from functools import cache

from kubernetes import client, config

NAMESPACE = 'cykube'


def init():
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        # we're inside a cluster
        config.load_incluster_config()
    else:
        # we're not
        config.load_kube_config()


@cache
def get_batch_api() -> client.BatchV1Api:
    return client.BatchV1Api()


@cache
def get_events_api() -> client.EventsV1Api:
    return client.EventsV1Api()


@cache
def get_core_api() -> client.CoreV1Api:
    return client.CoreV1Api()


def get_job_env():
    envs = []
    for key in ['API_TOKEN', 'MAIN_API_URL', 'AGENT_URL', 'CACHE_URL']:
        envs.append(client.V1EnvVar(name=key, value=os.environ.get(key)))
    return envs
