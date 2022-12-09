import enum


class PlatformEnum(str, enum.Enum):
    BITBUCKET = 'bitbucket'
    JIRA = 'jira'
    SLACK = 'slack'
    GITHUB = 'github'


class TestRunStatus(str, enum.Enum):
    started = 'started'
    cancelled = 'cancelled'
    running = 'running'
    timeout = 'timeout'
    failed = 'failed'
    passed = 'passed'


ACTIVE_STATES = [TestRunStatus.started, TestRunStatus.running]


class TestResultStatus(str, enum.Enum):
    passed = 'passed'
    skipped = 'skipped'
    failed = 'failed'


class AppWebSocketActions(str, enum.Enum):
    testrun = 'testrun'
    buildlog = 'buildlog'
    hub = 'hub'

