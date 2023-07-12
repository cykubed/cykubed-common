import uuid
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, validator, NonNegativeInt
from pydantic.fields import Field

from .enums import PlatformEnum, TestRunStatus, TestResultStatus, AppWebSocketActions, LogLevel, AgentEventType, \
    SpecFileStatus, AppFramework, KubernetesPlatform, TriggerType


class PaginationParams(BaseModel):
    page: NonNegativeInt
    pagesize: NonNegativeInt


class PaginatedModel(PaginationParams):
    total: NonNegativeInt


#
# Auth
#

class IntegrationSummary(BaseModel):
    name: PlatformEnum
    login: Optional[str]
    user_id: Optional[int]
    allow_user_repositories: Optional[bool]

    class Config:
        orm_mode = True


class SubscriptionType(BaseModel):
    name: str
    free_tests: Optional[int] = None
    users_limit: Optional[int] = None
    artifact_ttl: Optional[int] = None
    fully_managed: bool = False

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
    tests_remaining: Optional[int]
    subscription: Subscription

    class Config:
        orm_mode = True


class UserOrganisationSummary(BaseModel):
    organisation_id: int
    organisation_name: str
    is_admin: Optional[bool]

    class Config:
        orm_mode = True


class UserUISettingsModel(BaseModel):
    current_org_id: Optional[int]
    last_git_org_id: Optional[str]
    last_git_platform: Optional[PlatformEnum]
    page_size: Optional[int]

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    """
    User in a particular organisation
    """
    id: int
    name: str
    avatar_url: Optional[str]
    email: str
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    name: str
    avatar_url: Optional[str]
    token: uuid.UUID
    email: str
    uisettings: UserUISettingsModel
    # allow_user_repositories: bool = False
    # integrations: list[IntegrationSummary]
    organisations: list[UserOrganisationSummary]

    class Config:
        orm_mode = True


class UserInvite(BaseModel):
    email: str
    is_admin: Optional[bool]


class UserEmail(BaseModel):
    email: str


class UserUpdate(BaseModel):
    is_admin: bool


class APIToken(BaseModel):
    id: int
    token: uuid.UUID
    created: datetime

    class Config:
        orm_mode = True


class OAuthCodeRespose(BaseModel):
    code: str


class OAuthPostInstall(BaseModel):
    token: Optional[str]
    app_installed: Optional[bool]  # For Github
    profile: UserProfile


class AgentConnectionRequest(BaseModel):
    host_name: str


#
# Test results
#

class UploadResult(BaseModel):
    urls: list[str]


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
    code_frame: Optional[CodeFrame]
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
    timeout: Optional[bool] = False


class ResultSummary(BaseModel):
    total: int = 0
    skipped: int = 0
    passes: int = 0
    failures: int = 0


class OrganisationIn(BaseModel):
    name: str
    auto_signup_domain: Optional[str]
    project_auto_signup: bool


class NewProject(BaseModel):
    name: str
    organisation_id: Optional[int] # although we'll through an error if the user has > 1 org

    owner: Optional[str]

    framework: AppFramework = AppFramework.generic
    default_branch: str
    platform: PlatformEnum
    url: str
    parallelism: int = 10
    checks_integration: bool = True

    agent_id: Optional[int] = None

    spot_enabled: bool = False
    spot_percentage: int = 80

    browser: str = None

    spec_deadline: Optional[int] = None
    spec_filter: Optional[str] = None

    build_cmd: str
    build_cpu: float = 2
    build_memory: float = 4
    build_deadline: int = 10*60
    build_ephemeral_storage: int = 4
    build_storage: int = 10

    start_runners_first: bool
    runner_image: Optional[str]
    runner_cpu: float = 2
    runner_memory: float = 4
    runner_deadline: int = 3600
    runner_ephemeral_storage: int = 1

    timezone: str = 'UTC'
    cypress_retries: int = 2

    class Config:
        orm_mode = True


class Project(NewProject):
    id: int

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


class GitOrganisation(BaseModel):
    id: int
    name: str
    platform_id: Optional[str]
    login: str

    class Config:
        orm_mode = True


class Repository(BaseModel):
    id: str
    owner: str
    name: str
    url: str
    platform: PlatformEnum
    default_branch: Optional[str]
    pushed_at: Optional[datetime]
    git_organisation: Optional[GitOrganisation]
    user_id: Optional[int]

    class Config:
        orm_mode = True


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
    storage_size: int # Size in GB
    expires: datetime  # expiry date
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
    duration: Optional[int]
    total_tests: Optional[int]
    failed_tests: Optional[int]
    flakey_tests: Optional[int]

    class Config:
        orm_mode = True


class TestRunSummary(TestRunCommon):

    class Config:
        orm_mode = True



class TestRunSummaries(PaginatedModel):
    items: list[TestRunSummary]


class TestRunErrorReport(BaseModel):
    stage: str
    msg: str
    error_code: Optional[int]

#
# Webhooks
#


class CommonTriggerModel(BaseModel):
    project_id: int
    name: Optional[str]
    on_pass: Optional[bool] = False
    on_fail: Optional[bool] = False
    on_fixed: Optional[bool] = False
    branch_regex: Optional[str]


class NewWebHook(CommonTriggerModel):
    url: str


class WebHook(NewWebHook):
    id: int

    class Config:
        orm_mode = True


class NewNotification(CommonTriggerModel):
    platform: PlatformEnum
    channel_id: str
    channel_name: str


class Notification(NewNotification):
    id: int

    class Config:
        orm_mode = True




#
# TestRun detail
#

class TestRunJobStats(BaseModel):
    total_build_seconds: Optional[int]
    total_runner_seconds: Optional[int]

    total_cpu_seconds: Optional[int]
    total_memory_gb_seconds: Optional[int]
    total_ephemeral_gb_seconds: Optional[int]

    cpu_seconds_normal: Optional[int]
    memory_gb_seconds_normal: Optional[int]
    ephemeral_gb_seconds_normal: Optional[int]

    cpu_seconds_spot: Optional[int]
    memory_gb_seconds_spot: Optional[int]
    ephemeral_gb_seconds_spot: Optional[int]

    class Config:
        orm_mode = True


class TestRunDetail(TestRunCommon):
    files: Optional[list[SpecFile]]
    duration: Optional[int]
    jobstats: Optional[TestRunJobStats] = None

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


class WebHookPayload(BaseModel):
    trigger: TriggerType
    testrun: TestRunDetail


class NewAgentModel(BaseModel):
    organisation_id: int


class UpdatedAgentModel(BaseModel):
    name: Optional[str] = 'Agent'
    platform: Optional[KubernetesPlatform] = KubernetesPlatform.generic
    replication: str = 'replicated'


class AgentModel(UpdatedAgentModel, NewAgentModel):
    id: int
    token: uuid.UUID
    name: str
    first_connected: Optional[datetime]
    version: Optional[str]
    connected: int = 0

    class Config:
        orm_mode = True


class SlackChannel(BaseModel):
    id: str
    public: bool
    name: str


class SlackChannels(BaseModel):
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
    action: AppWebSocketActions = AppWebSocketActions.agent
    agent: AgentModel


class TestRunErrorMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.error
    message: str
    source: str


class TestRunDetailUpdateMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.testrun
    testrun: TestRunDetail


class SpecFileMessage(BaseAppSocketMessage):
    testrun_id: int
    spec: SpecFile


class SpecFileLogMessage(BaseAppSocketMessage, SpecFileLog):
    action: AppWebSocketActions = AppWebSocketActions.spec_log_update


class TestRunStatusUpdateMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.status
    testrun_id: int
    status: TestRunStatus


class AppLogMessage(BaseModel):
    source: str
    ts: datetime
    level: LogLevel
    msg: str
    host: Optional[str]
    step: Optional[int]

    def __str__(self):
        return self.msg


class LogUpdateMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.buildlog
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


class AgentTestRunErrorEvent(AgentEvent):
    type: AgentEventType = AgentEventType.error
    report: TestRunErrorReport


class AgentRunComplete(AgentEvent):
    type: AgentEventType = AgentEventType.run_completed


class AgentBuildCompletedEvent(AgentEvent):
    type: AgentEventType = AgentEventType.build_completed
    specs: list[str]


class AgentLogMessage(AgentEvent):
    type: AgentEventType = AgentEventType.log
    msg: AppLogMessage


class AgentErrorMessage(AgentEvent):
    type: AgentEventType = AgentEventType.error
    source: str
    message: str



