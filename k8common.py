import os

from kubernetes import client, config

NAMESPACE = 'cykube'


def init():
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        # we're inside a cluster
        config.load_incluster_config()
    else:
        # we're not
        config.load_kube_config()


def get_job_env():
    return [client.V1EnvVar(name='API_TOKEN', value=os.environ.get('API_TOKEN')),
            client.V1EnvVar(name='AGENT_URL', value='http://cykube:5000'),
            client.V1EnvVar(name='CACHE_URL', value='http://cache'),
            client.V1EnvVar(name='MAIN_API_URL', value=os.environ.get('MAIN_API_URL',
                                                                      'https://app.cykube.net/api'))
            ]
