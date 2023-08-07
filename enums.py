import enum


class Currency(str, enum.Enum):
    usd = 'usd'
    gbp = 'gbp'
    eur = 'eur'


class ErrorType(str, enum.Enum):
    quota_exceeded = 'quota_exceeded'
    payment_gateway_error = 'payment_gateway_error'


class AppFramework(str, enum.Enum):
    angular = 'angular'
    vue = 'vue'
    nextjs = 'next.js'
    generic = 'generic'


class VersionType(str, enum.Enum):
    major = 'major'
    minor = 'minor'
    patch = 'patch'


class ImageType(str, enum.Enum):
    agent = 'agent'
    runner = 'runner'


class JobType(str, enum.Enum):
    builder = 'builder'
    runner = 'runner'


class Region(str, enum.Enum):
    europe = 'europe'
    us = 'us'
    uk = 'uk'


class PlatformEnum(str, enum.Enum):
    BITBUCKET = 'bitbucket'
    JIRA = 'jira'
    SLACK = 'slack'
    GITHUB = 'github'


class PlatformType(str, enum.Enum):
    git = 'git'
    messaging = 'messaging'


GIT_PLATFORMS = [PlatformEnum.GITHUB,
                 PlatformEnum.BITBUCKET]


NOTIFICATION_PLATFORMS = [PlatformEnum.SLACK]


class GitOrgTypeEnum(str, enum.Enum):
    user = 'user'
    org = 'organisation'


class TestRunStatus(str, enum.Enum):
    __test__ = False

    pending = 'pending'
    started = 'started'
    building = 'building'
    cancelled = 'cancelled'
    running = 'running'
    passed = 'passed'
    timeout = 'timeout'
    failed = 'failed'


class SpecFileStatus(str, enum.Enum):
    started = 'started'
    passed = 'passed'
    failed = 'failed'
    timeout = 'timeout'
    cancelled = 'cancelled'


class NotificationStates(str, enum.Enum):
    failed = 'failed'
    passed = 'passed'
    timeout = 'timeout'


class AgentEventType(str, enum.Enum):
    log = 'log'
    build_completed = 'build_completed'
    cache_prepared = 'cache_prepared'
    run_completed = 'run_completed'
    error = 'error'


class TestRunSource(str, enum.Enum):
    webhook = 'webhook'
    web_start = 'web_start'
    web_rerun = 'web_rerun'


ACTIVE_STATES = [TestRunStatus.pending, TestRunStatus.started, TestRunStatus.building, TestRunStatus.running]
INACTIVE_STATES = [TestRunStatus.cancelled, TestRunStatus.failed, TestRunStatus.passed, TestRunStatus.timeout]


class KubernetesPlatform(str, enum.Enum):
    generic = 'generic'
    gke = 'gke'
    eks = 'eks'
    minikube = 'minikube'


PLATFORMS_SUPPORTING_SPOT = [KubernetesPlatform.gke]


class TestResultStatus(str, enum.Enum):
    passed = 'passed'
    skipped = 'skipped'
    failed = 'failed'


class AppWebSocketActions(str, enum.Enum):
    testrun = 'testrun'
    jobstats = 'jobstats'
    status = 'status'
    spec_started = 'spec-started'
    spec_finished = 'spec-finished'
    spec_log_update = 'spec-log-update'
    buildlog = 'buildlog'
    agent = 'agent'
    error = 'error'
    payment_failed = 'payment-failed'
    plan_upgrade_successful = 'plan-upgrade-successful'


class AgentWebsocketActions(str, enum.Enum):
    log = 'log'
    status = 'status'


class LogLevel(str, enum.Enum):
    debug = 'debug'
    info = 'info'
    cmd = 'cmd'
    cmdout = 'cmdout'
    warning = 'warning'
    error = 'error'


class TriggerType(str, enum.Enum):
    passed = 'passed'
    failed = 'failed'
    fixed = 'fixed'


loglevelToInt = {LogLevel.debug: 0,
                 LogLevel.info: 1,
                 LogLevel.cmd: 1,
                 LogLevel.cmdout: 1,
                 LogLevel.warning: 2,
                 LogLevel.error: 3}
