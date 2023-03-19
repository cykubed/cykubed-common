from pydantic import BaseSettings


class AppSettings(BaseSettings):
    API_TOKEN: str = 'cykubeauth'
    AGENT_NAME: str = 'default'

    K8: bool = True

    NAMESPACE = 'cykube'

    SERVER_START_TIMEOUT: int = 60
    CYPRESS_RUN_TIMEOUT: int = 10*60

    # keep app distributions for 1 hr in case of reruns
    APP_DISTRIBUTION_CACHE_TTL: int = 3600
    # keep the node distributions for 30 days
    NODE_DISTRIBUTION_CACHE_TTL: int = 30*3600

    ENCODING = 'utf8'

    BUILD_TIMEOUT: int = 900
    NODE_PATH: str = None

    TEST = False

    MAX_HTTP_RETRIES = 10
    MESSAGE_POLL_PERIOD = 1

    AGENT_URL: str = 'http://127.0.0.1:5000'
    CACHE_URL: str = 'http://127.0.0.1:5001'
    MAIN_API_URL: str = 'https://app.cykube.net/api'

    BUILD_DIR = '/tmp/cykube/build'
    RESULTS_FOLDER = '/tmp/cykube/results'
    CACHE_DIR: str = '/tmp/cykube/cache'

    SENTRY_DSN: str = None

    HOSTNAME: str = None  # for testin

    REDIS_HOST = 'localhost'
    REDIS_PASSWORD = ''

    FILESTORE_SERVERS: str = 'localhost:8100'  # comma-delimeted list
    FILESTORE_CACHE_SIZE: int = 10*1024*1024*1024  # 10GB cache suze
    FILESTORE_TOTAL_TIMEOUT: int = 600
    FILESTORE_CONNECT_TIMEOUT: int = 10
    FILESTORE_READ_TIMEOUT: int = 300
    FILESTORE_DISK_SIZE_GB: float = 10.0
    FILESTORE_MIN_WRITE: int = 2
    FILESTORE_SYNC_PERIOD: int = 60*10
    CHUNK_SIZE: int = 8192*8


settings = AppSettings()


