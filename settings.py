from pydantic import BaseSettings


class AppSettings(BaseSettings):
    API_TOKEN: str = 'cykubeauth'
    AGENT_NAME: str = 'default'

    K8: bool = True

    NAMESPACE = 'cykube'

    TEST_RUN_TIMEOUT: int = 30 * 60
    SPEC_FILE_TIMEOUT: int = 5 * 60

    JOB_TTL = 3600
    DEFAULT_BUILD_JOB_DEADLINE = 2 * 60
    JOB_STATUS_POLL_PERIOD = 10

    DEFAULT_RUNNER_JOB_DEADLINE = 3600

    DIST_BUILD_TIMEOUT: int = 10 * 60
    SERVER_START_TIMEOUT: int = 10 * 60
    SERVER_PORT: int = 8000
    CYPRESS_RUN_TIMEOUT: int = 10*60

    ENCODING = 'utf8'

    BUILD_TIMEOUT: int = 900

    TEST = False

    MONGO_URL = 'mongodb://localhost:27017'
    MONGO_DATABASE = 'cykube'

    AGENT_URL: str = 'http://127.0.0.1:5000'
    CACHE_URL: str = 'http://127.0.0.1:5001'
    MAIN_API_URL: str = 'https://app.cykube.net/api'
    BUILD_DIR = '/tmp/cykube/build'
    RESULTS_FOLDER = '/tmp/cykube/results'

    SENTRY_DSN: str = None

    DIST_CACHE_STATENESS_WINDOW_DAYS: int = 7

    CYKUBE_CACHE_DIR: str = '/var/lib/cykubecache'


settings = AppSettings()
