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


class AgentEventType(str, enum.Enum):
    log = 'log'
    build_completed = 'build_completed'
    spec_completed = 'spec_completed'

    status = 'status'
    completed = 'completed'


ACTIVE_STATES = [TestRunStatus.started, TestRunStatus.building, TestRunStatus.running]
INACTIVE_STATES = [TestRunStatus.cancelled, TestRunStatus.failed, TestRunStatus.passed, TestRunStatus.timeout]


class TestResultStatus(str, enum.Enum):
    passed = 'passed'
    skipped = 'skipped'
    failed = 'failed'


class AppWebSocketActions(str, enum.Enum):
    testrun = 'testrun'
    status = 'status'
    specfile = 'specfile'
    buildlog = 'buildlog'
    agent = 'agent'


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


loglevelToInt = {LogLevel.debug: 0,
                 LogLevel.info: 1,
                 LogLevel.cmd: 1,
                 LogLevel.cmdout: 1,
                 LogLevel.warning: 2,
                 LogLevel.error: 3}
