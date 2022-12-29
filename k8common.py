import os

from kubernetes import client, config

batchapi = None
NAMESPACE = 'cykube'


def get_batch_api() -> client.BatchV1Api:
    global batchapi
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        # we're inside a cluster
        config.load_incluster_config()
        batchapi = client.BatchV1Api()
    else:
        # we're not
        config.load_kube_config()
        batchapi = client.BatchV1Api()
    return batchapi


def get_job_env():
    return [client.V1EnvVar(name='API_TOKEN', value=os.environ.get('API_TOKEN'))]
