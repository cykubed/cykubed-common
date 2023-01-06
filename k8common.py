import os

import pystache
import yaml
from kubernetes import client, config, utils
from kubernetes.utils import FailToCreateError
from loguru import logger

from .schemas import NewTestRun

NAMESPACE = os.environ.get('NAMESPACE', 'cykube')


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


def create_jobs(templates_files, testrun: NewTestRun):
    context = {
        'image': testrun.project.runner_image,
        'cpu': testrun.project.build_cpu,
        'memory': testrun.project.build_memory,
        'testrun_id': testrun.id,
        'token': os.environ['API_TOKEN'],
        'branch': testrun.branch
    }
    yaml_objects = [yaml.safe_load(pystache.render(f, context)) for f in templates_files]
    try:
        utils.create_from_yaml(client.ApiClient(), yaml_objects=yaml_objects)
    except FailToCreateError:
        logger.exception('Failed to create Job', trid=testrun.id)
