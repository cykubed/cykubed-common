from pydantic import BaseSettings


class AppSettings(BaseSettings):
    API_TOKEN: str = 'cykubeauth'
    AGENT_NAME: str = 'default'

    K8: bool = True

    NAMESPACE = 'cykube'

    TEST_RUN_TIMEOUT: int = 30 * 60
    SPEC_FILE_TIMEOUT: int = 5 * 60

    SERVER_START_TIMEOUT: int = 10 * 60
    CYPRESS_RUN_TIMEOUT: int = 10*60

    # keep app distributions for 1 hr in case of reruns
    APP_DISTRIBUTION_CACHE_TTL: int = 3600

    ENCODING = 'utf8'

    BUILD_TIMEOUT: int = 900
    NODE_PATH: str = None

    TEST = False

    MONGO_CONNECT_TIMEOUT = 60

    MAX_HTTP_RETRIES = 10

    MONGO_ROOT_PASSWORD = ''
    MONGO_HOST = 'cykube-mongodb-0.cykube-mongodb-headless'
    MONGO_USER = 'root'
    MONGO_DATABASE = 'cykube'

    AGENT_URL: str = 'http://127.0.0.1:5000'
    CACHE_URL: str = 'http://127.0.0.1:5001'
    MAIN_API_URL: str = 'https://app.cykube.net/api'
    BUILD_DIR = '/tmp/cykube/build'
    RESULTS_FOLDER = '/tmp/cykube/results'

    SENTRY_DSN: str = None

    ARCHIVE = False
    DIST_CACHE_STATENESS_WINDOW_DAYS: int = 7

    CYKUBE_CACHE_DIR: str = '/var/lib/cykubecache'


settings = AppSettings()
