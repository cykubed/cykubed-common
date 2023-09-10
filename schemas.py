import uuid
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, validator, NonNegativeInt, AnyHttpUrl, root_validator
from pydantic.fields import Field

from enums import (PlatformEnum, TestRunStatus, TestRunStatusFilter,
                    TestResultStatus, AppWebSocketActions, LogLevel, AgentEventType, \
                    SpecFileStatus, AppFramework, KubernetesPlatform, PlatformType, JobType, ErrorType, Currency, \
                    OrganisationDeleteReason, OnboardingState)


class DummyTestRunStatusFilter(BaseModel):
    filter: TestRunStatusFilter


class GenericError(BaseModel):
    type: ErrorType
    msg: Optional[str]


class Token(BaseModel):
    token: str


class PaginationParams(BaseModel):
    page: NonNegativeInt
    pagesize: NonNegativeInt


class PaginatedModel(PaginationParams):
    total: NonNegativeInt


#
# Auth
#

class RocketChatAuth(BaseModel):
    url: str
    user_id: str
    access_token: str


class IntegrationSummary(BaseModel):
    name: PlatformEnum
    type: PlatformType
    connected: bool = False
    login: Optional[str]
    user_id: Optional[int]
    app_installed: Optional[bool]  # For Github
    allow_user_repositories: Optional[bool]

    class Config:
        orm_mode = True


class Prices(BaseModel):
    currency: Currency
    flat_fee: float
    per_1k_tests: float
    per_10k_build_credits: float

    class Config:
        orm_mode = True


class SubscriptionPlan(BaseModel):
    name: str
    included_test_results: Optional[int] = None
    included_build_credits: Optional[int] = None
    max_days: Optional[int] = None
    users_limit: Optional[int] = None
    artifact_ttl: Optional[int] = None
    max_parallelism: Optional[int] = None

    class Config:
        orm_mode = True


class SelectedSubscriptionPlan(SubscriptionPlan, Prices):
    pass


class SelectedPlan(BaseModel):
    name: str
    currency: Currency


class StripeClientSecret(BaseModel):
    subscription_id: str
    client_secret: str


class SubscriptionPlanWithPrices(SubscriptionPlan):
    prices: list[Prices] = []

    class Config:
        orm_mode = True


class Subscription(BaseModel):
    started: date
    active: bool
    expires: Optional[date]
    plan: SubscriptionPlan
    cancelled: Optional[date]
    payment_failure_date: Optional[date]

    class Config:
        orm_mode = True


class OrganisationStripeDetails(BaseModel):
    """
    Only used internally for Stripe testing
    """
    frozen_time: Optional[datetime]


class AccountDetails(BaseModel):
    subscription: Subscription
    selected_plan: Optional[str]
    stripe_client_secret: Optional[str]
    new_stripe_subscription_id: Optional[str]
    new_subscription_id: Optional[int]
    test_results_used: int
    build_credits_used: int
    users: int


class OrganisationBase(BaseModel):
    id: int
    name: str
    prefer_self_host: bool


class Organisation(OrganisationBase):
    subscription: Optional[Subscription]

    class Config:
        orm_mode = True


class Country(BaseModel):
    name: str
    code: str


class StaffOrganisation(OrganisationBase):
    """
    Additional information available to staff users
    """
    account: AccountDetails
    stripe: Optional[OrganisationStripeDetails]


class StaffOrganisationList(PaginatedModel):
    items: list[StaffOrganisation]


class OrgTimeAdvance(BaseModel):
    timestamp: datetime


class Address(BaseModel):
    city: Optional[str]
    country: str = Field(..., max_length=2)
    line1: str = Field(..., max_length=255)
    line2: Optional[str] = Field(None, max_length=255)
    postal_code: Optional[str] = Field(None, max_length=255)
    state: Optional[str] = Field(None, max_length=255)

    class Config:
        orm_mode = True


class OrganisationUpdate(BaseModel):
    name: Optional[str]
    prefer_self_host: Optional[bool]
    onboarding_state: Optional[OnboardingState]
    address: Optional[Address]


class OrganisationDelete(BaseModel):
    """
    Post-org delete
    """
    token: str
    comments: Optional[str]
    reason: Optional[OrganisationDeleteReason]


class UserOrganisationSummary(BaseModel):
    id: int
    name: Optional[str]
    onboarding_state: OnboardingState
    address: Optional[Address]
    prefer_self_host: Optional[bool]
    is_admin: Optional[bool]

    class Config:
        orm_mode = True


class UserUISettingsModel(BaseModel):
    preferred_currency: Optional[Currency]
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
    id: int
    name: str
    avatar_url: Optional[str]
    token: uuid.UUID
    email: str
    uisettings: UserUISettingsModel
    account: Optional[AccountDetails]
    is_pending: bool
    is_staff: Optional[bool] = False
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


class OAuthCodeResponse(BaseModel):
    code: str
    organisation_id: Optional[int]
    orgtoken: Optional[str]


class OAuthPostInstall(BaseModel):
    integration: IntegrationSummary
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


class NewProject(BaseModel):
    name: str = Field(description="Project name i.e name of Git repository")
    organisation_id: int = Field(description="Owner organisation ID")

    owner: Optional[str]

    framework: AppFramework = AppFramework.generic
    default_branch: str = Field(description="Default branch")
    platform: PlatformEnum = Field(description="Git platform")
    url: str = Field(description="URL to git repository")
    parallelism: int = Field(description="Number of runner pods i.e the parallelism of the runner job",
                             default=4, ge=0, le=30)
    checks_integration: bool = True

    agent_id: Optional[int] = Field(description="ID of the agent that should be used to run this test. "
                                                "Only required for self-hosted agents")

    browser: str = None

    spec_deadline: Optional[int] = Field(
        description="Deadline in seconds to assign to an individual spec. If 0 then there will be no deadline set "
                    "(although the runner deadline still applies)",
        default=0,
        le=3600)
    spec_filter: Optional[str] = Field(description="Only test specs matching this regex")

    build_cmd: str = Field(description="Command used to build the app distribution")
    build_cpu: float = Field(description="Number of vCPU units to assign to the builder Job", default=2,
                             ge=2,
                             le=10)
    build_memory: float = Field(description="Amount of memory in GB to assign to the builder Pod", default=4,
                                ge=2, le=10)
    build_deadline: int = Field(description="Build deadline in seconds", default=10 * 60,
                                ge=60, le=3600)
    build_ephemeral_storage: int = Field(description="Build ephemeral storage in GB", default=4,
                                         ge=1, le=20)
    build_storage: int = Field(description="Build working storage size in GB", default=10,
                               ge=1, le=100)

    runner_image: Optional[str] = Field(
        description="Docker image to use in the runner. Can only be specified for self-hosted agents")
    runner_cpu: float = Field(description="Number of vCPU units to assign to each runner Pod", default=2,
                              ge=1,
                              le=10)
    runner_memory: float = Field(description="Amount of memory in GB to assign to each runner Pod", default=5,
                                 ge=2, le=10)
    runner_deadline: int = Field(description="Deadline in seconds to assign to the entire runner job", default=3600,
                                 ge=60, le=3 * 3600)
    runner_ephemeral_storage: int = Field(description="Runner ephemeral storage in GB", default=4,
                                          ge=1, le=20)

    timezone: str = Field(description="Timezone used in runners", default='UTC')
    cypress_retries: int = Field(
        description="Number of retries of failed tests. If 0 then default to any retry value set in the Cypress config file",
        default=0, le=10, ge=0)

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
    owner: Optional[str]
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
    branch: str
    sha: Optional[str]
    source: str = 'web_start'


class SpotEnabledModel(BaseModel):
    spot_percentage: int = Field(description="Percentage of runner pods that will be spot, if available",
                                 default=0, ge=0, le=100)


class NewTestRun(BaseTestRun, SpotEnabledModel):
    """
    Sent to the agent to kick off a run.
    """
    url: str
    project: Project
    preprovision: Optional[bool]
    status: Optional[TestRunStatus]

    class Config:
        orm_mode = True


class CacheItem(BaseModel):
    organisation_id: int
    name: str
    ttl: int  # TTL in secs
    storage_size: int  # Size in GB
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


class PodDuration(BaseModel):
    """
    Duration in seconds for a single pod
    """
    job_type: JobType
    is_spot: bool = False
    duration: int = 0


class AuthorModel(BaseModel):
    name: str
    email: str
    avatar_url: Optional[AnyHttpUrl]

    class Config:
        orm_mode = True


class CommitDetailsModel(BaseModel):
    author: AuthorModel
    message: str
    commit_url: str

    class Config:
        orm_mode = True


class TestRunCommon(BaseTestRun):
    status: TestRunStatus
    fixed: Optional[bool]
    error: Optional[str]
    started: Optional[datetime]
    finished: Optional[datetime] = None
    commit: Optional[CommitDetailsModel]
    duration: Optional[int]
    total_tests: Optional[int]
    failed_tests: Optional[int]
    flakey_tests: Optional[int]

    class Config:
        orm_mode = True


class TestRunSummary(TestRunCommon):
    project_id: int
    project_name: str

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
    organisation_id: int
    project_id: Optional[int]
    name: Optional[str]
    on_pass: Optional[bool] = False
    on_fail: Optional[bool] = False
    on_fixed: Optional[bool] = False
    on_flake: Optional[bool] = False
    branch_regex: Optional[str]

    @root_validator
    def check_triggers(cls, values):
        if (not values.get('on_pass') and not values.get('on_fail') and not values.get('on_flake') and
                not values.get('on_fixed')):
            raise ValueError('Specify at least one trigger')
        return values


class NewWebHook(CommonTriggerModel):
    url: str


class WebHook(NewWebHook):
    id: int
    project_name: Optional[str]

    class Config:
        orm_mode = True


class WebhookHistory(BaseModel):
    hook_id: int
    testrun_id: int
    created: datetime
    status_code: Optional[int]
    request: str
    response: Optional[str]
    error: Optional[str]

    class Config:
        orm_mode = True


class WebhookTesterResponse(BaseModel):
    testrun_id: int
    status: TestRunStatus


#
# Notifications
#

class NewNotification(CommonTriggerModel):
    platform: PlatformEnum
    channel_id: str
    channel_name: str
    include_private: bool = False


class Notification(NewNotification):
    id: int
    project_name: Optional[str]

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

    total_cost_usd: Optional[float]

    class Config:
        orm_mode = True


class KubernetesPlatformPricingModel(BaseModel):
    platform: KubernetesPlatform
    updated: datetime
    region: str
    cpu_spot_price: Optional[float]
    cpu_normal_price: Optional[float]
    memory_spot_price: Optional[float]
    memory_normal_price: Optional[float]
    ephemeral_price: Optional[float]

    class Config:
        orm_mode = True


class TestRunDetail(TestRunCommon):
    project: Project
    files: Optional[list[SpecFile]]
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


class NewAgentModel(BaseModel):
    organisation_id: int


class UpdatedAgentModel(SpotEnabledModel):
    name: Optional[str] = 'A'
    platform: Optional[KubernetesPlatform] = KubernetesPlatform.generic
    replicated: Optional[bool] = False
    platform_project_id: Optional[str]
    preprovision: Optional[bool]

    service_account: Optional[str]
    is_public: Optional[bool]


class AgentModel(UpdatedAgentModel, NewAgentModel):
    id: int
    token: uuid.UUID
    name: str
    first_connected: Optional[datetime]
    version: Optional[str]
    connected: int = 0
    is_public: Optional[bool]

    class Config:
        orm_mode = True


class NotificationChannel(BaseModel):
    id: str
    public: Optional[bool]
    name: str


class NotificationChannels(BaseModel):
    channels: list[NotificationChannel]


class TestRunJobStatus(BaseModel):
    name: str
    status: str
    message: Optional[str]


class PodStatus(BaseModel):
    pod_name: str
    project_id: int
    testrun_id: int
    phase: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    is_spot: bool
    duration: Optional[int]
    job_type: str


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


class SubscriptionUpdatedMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.subscription_updated
    subscription: Subscription


class SpecFileMessage(BaseAppSocketMessage):
    testrun_id: int
    spec: SpecFile


class WebhookNotifiedMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.webhook_notified
    details: WebhookHistory


class SpecFileLogMessage(BaseAppSocketMessage, SpecFileLog):
    action: AppWebSocketActions = AppWebSocketActions.spec_log_update


class TestRunStatusUpdateMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.status
    testrun_id: int
    status: TestRunStatus


class TestRunJobStatsUpdateMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.jobstats
    testrun_id: int
    stats: TestRunJobStats


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

