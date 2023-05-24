import uuid
from datetime import date, datetime
from typing import Optional, List, Union

from pydantic import BaseModel, validator
from pydantic.fields import Field

from .enums import PlatformEnum, TestRunStatus, TestResultStatus, AppWebSocketActions, LogLevel, AgentEventType, \
    SpecFileStatus, TriggerType


#
# Auth
#

class IntegrationSummary(BaseModel):
    name: PlatformEnum
    user_id: Optional[int]


class UserProfile(BaseModel):
    name: str
    avatar_url: Optional[str]
    token: str
    email: str
    integrations: list[IntegrationSummary]
    organisation_id:  int
    organisation_name: str
    is_admin: bool
    integration_user_id: Optional[int]


class APIToken(BaseModel):
    id: int
    token: uuid.UUID
    created: datetime

    class Config:
        orm_mode = True


class OAuthCodeRespose(BaseModel):
    code: str


class OAuthPostInstall(BaseModel):
    profile: UserProfile
    token: Optional[str]
    app_installed: Optional[bool]  # For Github


class AgentConnectionRequest(BaseModel):
    host_name: str


#
# Test results
#


class CodeFrame(BaseModel):
    file: Optional[str]  # TODO make this required
    line: int
    column: int
    frame: str
    language: str


class TestResultError(BaseModel):
    title: str
    type: Optional[str]
    test_line: Optional[int]
    message: str
    stack: str
    code_frame: CodeFrame
    video: Optional[str]


class TestResult(BaseModel):
    title: str
    context: str
    status: TestResultStatus
    retry: int = 0
    duration: Optional[int]
    failure_screenshots: Optional[list[str]]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error: Optional[TestResultError]


class SpecResult(BaseModel):
    tests: List[TestResult]
    video: Optional[str]


class ResultSummary(BaseModel):
    total: int = 0
    skipped: int = 0
    passes: int = 0
    failures: int = 0


class OrganisationIn(BaseModel):
    name: str


class OrganisationSummary(BaseModel):
    id: int
    name: str


class SubscriptionType(BaseModel):
    name: str
    tests_limit: int
    users_limit: int

    class Config:
        orm_mode = True


class Subscription(BaseModel):
    started: date
    subtype: SubscriptionType
    finished: Optional[date]

    class Config:
        orm_mode = True


class Organisation(BaseModel):
    id: int
    name: str
    tests_used: int
    tests_remaining: int
    subscription: Subscription

    class Config:
        orm_mode = True


class NewProject(BaseModel):
    name: str
    owner: Optional[str]
    default_branch: str
    platform: PlatformEnum
    url: str
    parallelism: int = 10
    checks_integration: bool = True
    slack_channel_id: Optional[str]
    notify_on_passed: Optional[Union[bool, None]] = False

    agent_id: Optional[int] = None

    spot_enabled: bool = False
    spot_percentage: int = 80

    browser: str = None

    spec_deadline: Optional[int] = None

    build_cmd = 'ng build --output-path=dist'
    build_cpu: float = 2
    build_memory: float = 4
    build_deadline: int = 10*60
    build_ephemeral_storage: float = 10.0

    start_runners_first: bool
    runner_image: Optional[str]
    runner_cpu: float = 2
    runner_memory: float = 4
    runner_deadline: int = 3600
    runner_ephemeral_storage: float = 10.0

    timezone: str = 'UTC'
    cypress_retries: int = 2

    class Config:
        orm_mode = True


class Project(NewProject):
    id: int
    organisation: OrganisationSummary
    is_angular: bool = False

    class Config:
        orm_mode = True


class NewRunnerImage(BaseModel):
    tag: str = Field(description="Docker image tag")
    node_version: str = Field(description="Node version")
    description: Optional[str] = Field(description="Description")
    chrome: Optional[bool] = Field(description="True if this image contains Chrome", default=True)
    firefox: Optional[bool] = Field(description="True if this image contains Firefox", default=False)
    edge: Optional[bool] = Field(description="True if this image contains Edge", default=False)

    class Config:
        orm_mode = True


class NewRunnerImages(BaseModel):
    images: list[NewRunnerImage] = Field(description="List of Docker images")
    replace: bool = Field(description="If true then replace all existing images with this list", default=False)


class RunnerImage(NewRunnerImage):
    id: int

    class Config:
        orm_mode = True


class Workspace(BaseModel):
    slug: str
    name: str


class Repository(BaseModel):
    id: str
    name: str
    url: str
    owner: str
    owner_avatar_url: Optional[str]
    workspace_slug: Optional[str]
    pushed_at: Optional[datetime]
    platform: PlatformEnum
    default_branch: Optional[str]


class PendingAuthorisation(BaseModel):
    platform: PlatformEnum
    redirect_uri: Optional[str]


class AppInstallationState(BaseModel):
    installed: bool


class TestRunSpec(BaseModel):
    id: int
    file: str

    class Config:
        orm_mode = True


class TestRunStatusUpdate(BaseModel):
    status: TestRunStatus


class BaseTestRun(BaseModel):
    id: int
    local_id: int
    project: Project
    branch: str
    sha: Optional[str]
    status: str = 'started'
    source: str = 'web_start'


class NewTestRun(BaseTestRun):
    """
    Sent to the agent to kick off a run.
    """
    url: str

    class Config:
        orm_mode = True


class CacheItem(BaseModel):
    name: str
    ttl: int  # TTL in secs
    expires: datetime  # expiry date
    node_snapshot: Optional[str]
    specs: Optional[list[str]]


class TestRunUpdate(BaseModel):
    started: datetime
    finished: Optional[datetime] = None

    status: TestRunStatus


class SpecFile(BaseModel):
    file: str
    status: Optional[SpecFileStatus]
    pod_name: Optional[str]
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    termination_count: Optional[int] = 0
    duration: Optional[int]
    failures: int = 0
    result: Optional[SpecResult]

    class Config:
        orm_mode = True


class SpecFileName(BaseModel):
    file: str


class SpecFileLog(BaseModel):
    file: str
    log: str

    class Config:
        orm_mode = True


class CompletedSpecFile(BaseModel):
    file: str
    finished: datetime
    result: SpecResult


class TestRunCompleted(BaseModel):
    testrun_id: int
    total_build_duration: int = 0
    total_build_duration_spot: int = 0
    total_runner_duration: int = 0
    total_runner_duration_spot: int = 0


class AuthorModel(BaseModel):
    name: str
    email: str
    avatar_url: Optional[str]

    class Config:
        orm_mode = True


class CommitDetailsModel(BaseModel):
    author: AuthorModel
    message: str
    commit_url: str

    class Config:
        orm_mode = True


class TestRunCommon(BaseTestRun):
    error: Optional[str]
    started: Optional[datetime]
    finished: Optional[datetime] = None
    status: TestRunStatus
    commit: Optional[CommitDetailsModel]

    class Config:
        orm_mode = True


class TestRunSummary(TestRunCommon):
    progress_percentage: Optional[int]
    duration: Optional[int]

    class Config:
        orm_mode = True


class TestRunFailureReport(BaseModel):
    stage: str
    msg: str
    error_code: Optional[int]

#
# Webhooks
#


class NewWebHook(BaseModel):
    name: str
    trigger_type: Optional[TriggerType] = TriggerType.passed
    branch_regex: str
    url: str


class WebHook(NewWebHook):
    id: int
    project_id: int

    class Config:
        orm_mode = True


#
# TestRun detail
#


class TestRunDetail(TestRunCommon):
    files: Optional[list[SpecFile]]
    duration: Optional[int]
    terminations: int = 0
    build_started: Optional[datetime]
    build_seconds: Optional[int] = 0
    runner_seconds: Optional[int] = 0
    cpu_seconds_used: Optional[int] = 0
    memory_gb_seconds_used: Optional[int] = 0
    ephemeral_gb_seconds_used: Optional[int] = 0

    @validator('files', pre=True)
    def _iter_to_list(cls, v):
        """
        It's not entirely obvious why I need this, as according to the docs this should serialize fine.
        However, without this Pydantic will complain as v isn't a list
        :param v:
        :return:
        """
        return list(v or [])

    class Config:
        orm_mode = True


class NewAgentModel(BaseModel):
    name: Optional[str] = 'Agent'


class AgentModel(NewAgentModel):
    id: int
    token: uuid.UUID
    name: str
    first_connected: Optional[datetime]
    connected: int = 0

    class Config:
        orm_mode = True


class SlackChannel(BaseModel):
    id: str
    name: str


class SlackChannels(BaseModel):
    next_cursor: Optional[str]
    channels: list[SlackChannel]


class TestRunJobStatus(BaseModel):
    name: str
    status: str
    message: Optional[str]


#
# App messages
#

class BaseAppSocketMessage(BaseModel):
    action: AppWebSocketActions

    def __str__(self):
        return f'{self.action} msg'


class AgentStateMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.agent
    agent: AgentModel


class TestRunErrorMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.error
    message: str
    source: str


class TestRunDetailUpdateMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.testrun
    testrun: TestRunDetail


class SpecFileMessage(BaseAppSocketMessage):
    testrun_id: int
    spec: SpecFile


class SpecFileLogMessage(BaseAppSocketMessage, SpecFileLog):
    action = AppWebSocketActions.spec_log_update


class TestRunStatusUpdateMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.status
    testrun_id: int
    status: TestRunStatus


class AppLogMessage(BaseModel):
    source: str
    ts: datetime
    level: LogLevel
    msg: str
    step: Optional[int]

    def __str__(self):
        return self.msg


class LogUpdateMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.buildlog
    testrun_id: int
    line_num: int
    msg: AppLogMessage


class AgentBuildStarted(BaseModel):
    started: datetime


class AgentBuildCompleted(BaseModel):
    specs: list[str]


class AgentRunnerStopped(BaseModel):
    # duration in seconds
    duration: int
    terminated: bool = False


class AgentSpecCompleted(BaseModel):
    file: str
    finished: datetime
    result: SpecResult


class AgentSpecStarted(BaseModel):
    file: str
    pod_name: Optional[str]
    started: datetime


#
# Agent websocket
#

class AgentEvent(BaseModel):
    type: AgentEventType
    duration: Optional[int]
    testrun_id: int
    error_code: Optional[int]


class AgentTestRunFailedEvent(AgentEvent):
    type = AgentEventType.build_failed
    report: TestRunFailureReport


class AgentRunComplete(AgentEvent):
    type = AgentEventType.run_completed


class AgentCloneCompletedEvent(AgentEvent):
    type = AgentEventType.clone_completed
    cache_key: str
    specs: list[str]


class AgentLogMessage(AgentEvent):
    type = AgentEventType.log
    msg: AppLogMessage


class AgentErrorMessage(AgentEvent):
    type = AgentEventType.error
    source: str
    message: str



