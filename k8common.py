import os

from kubernetes import client, config

batchapi = None
NAMESPACE = 'cykube'


def init():
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        # we're inside a cluster
        config.load_incluster_config()
    else:
        # we're not
        config.load_kube_config()


def get_batch_api() -> client.BatchV1Api:
    return client.BatchV1Api()


def get_job_env():
    envs = []
    for key in ['API_TOKEN', 'MAIN_API_URL']:
        envs.append(client.V1EnvVar(name=key, value=os.environ.get(key)))
    envs += [client.V1EnvVar(name='AGENT_URL', value='http://cykube:5000'),
             client.V1EnvVar(name='CACHE_URL', value='http://cache')
             ]
    return envs
