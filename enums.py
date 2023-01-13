import enum


class PlatformEnum(str, enum.Enum):
    BITBUCKET = 'bitbucket'
    JIRA = 'jira'
    SLACK = 'slack'
    GITHUB = 'github'


class TestRunStatus(str, enum.Enum):
    started = 'started'
    building = 'building'
    cancelled = 'cancelled'
    running = 'running'
    timeout = 'timeout'
    failed = 'failed'
    passed = 'passed'


class NotificationStates(str, enum.Enum):
    failed = 'failed'
    passed = 'passed'
    timeout = 'timeout'


ACTIVE_STATES = [TestRunStatus.started, TestRunStatus.building, TestRunStatus.running]


class TestResultStatus(str, enum.Enum):
    passed = 'passed'
    skipped = 'skipped'
    failed = 'failed'


class AppWebSocketActions(str, enum.Enum):
    testrun = 'testrun'
    specfile = 'specfile'
    buildlog = 'buildlog'
    hub = 'hub'


class AgentWebsocketActions(str, enum.Enum):
    log = 'log'
    status = 'status'


class LogLevel(str, enum.Enum):
    debug = 'debug'
    info = 'info'
    warning = 'warning'
    error = 'error'
    critical = 'critical'

