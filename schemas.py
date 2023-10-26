import uuid
from datetime import date, datetime
from typing import Optional, List

from pydantic import field_validator, ConfigDict, BaseModel, NonNegativeInt, AnyHttpUrl, model_validator
from pydantic.fields import Field

from .enums import (PlatformEnum, TestRunStatus, TestRunStatusFilter,
                    TestResultStatus, AppWebSocketActions, LogLevel, AgentEventType, \
                    SpecFileStatus, AppFramework, KubernetesPlatform, PlatformType, JobType, ErrorType, Currency, \
                    OrganisationDeleteReason, OnboardingState)


class DummyTestRunStatusFilter(BaseModel):
    filter: TestRunStatusFilter


class GenericError(BaseModel):
    type: ErrorType
    msg: Optional[str] = None


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
    login: Optional[str] = None
    user_id: Optional[int] = None
    app_installed: Optional[bool] = None  # For Github
    allow_user_repositories: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class Prices(BaseModel):
    currency: Currency
    flat_fee: float
    per_1k_tests: float
    per_10k_build_credits: float
    model_config = ConfigDict(from_attributes=True)


class SubscriptionPlan(BaseModel):
    name: str
    included_test_results: Optional[int] = None
    included_build_credits: Optional[int] = None
    max_days: Optional[int] = None
    users_limit: Optional[int] = None
    artifact_ttl: Optional[int] = None
    max_parallelism: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


class Subscription(BaseModel):
    started: Optional[datetime] = None
    active: bool
    expires: Optional[date] = None
    plan: SubscriptionPlan
    cancelled: Optional[datetime] = None
    payment_failure_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class OrganisationStripeDetails(BaseModel):
    """
    Only used internally for Stripe testing
    """
    frozen_time: Optional[datetime] = None


class AccountDetails(BaseModel):
    subscription: Subscription
    selected_plan: Optional[str] = None
    stripe_client_secret: Optional[str] = None
    new_stripe_subscription_id: Optional[str] = None
    new_subscription_id: Optional[int] = None
    test_results_used: int
    build_credits_used_this_month: Optional[float] = None
    build_credits_remaining_before_topup: Optional[float] = None
    users: int

    payment_failed: Optional[bool] = None
    exceeded_free_plan: Optional[bool] = None


class OrganisationBase(BaseModel):
    id: int
    name: str
    prefer_self_host: bool
    model_config = ConfigDict(from_attributes=True)


class Country(BaseModel):
    name: str
    code: str


class AdminOrganisation(OrganisationBase):
    """
    Additional information available to staff users
    """
    account: AccountDetails
    stripe: Optional[OrganisationStripeDetails] = None


class IdName(BaseModel):
    id: int
    name: str


class AdminUser(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    is_pending: bool
    created: datetime
    organisations: Optional[list[IdName]] = None
    model_config = ConfigDict(from_attributes=True)


class AdminUserList(PaginatedModel):
    items: list[AdminUser]


class AdminOrganisationList(PaginatedModel):
    items: list[AdminOrganisation]


class AdminOrgPlanChange(BaseModel):
    plan: str
    expires: Optional[date] = None


class BuildCredits(BaseModel):
    credits: int


class OrgTimeAdvance(BaseModel):
    timestamp: datetime


class Address(BaseModel):
    city: Optional[str] = None
    country: str = Field(..., max_length=2)
    line1: str = Field(..., max_length=255)
    line2: Optional[str] = Field(None, max_length=255)
    postal_code: Optional[str] = Field(None, max_length=255)
    state: Optional[str] = Field(None, max_length=255)
    model_config = ConfigDict(from_attributes=True)


class OrganisationUpdate(BaseModel):
    name: Optional[str] = None
    prefer_self_host: Optional[bool] = None
    onboarding_state: Optional[OnboardingState] = None
    address: Optional[Address] = None


class OrganisationDelete(BaseModel):
    """
    Post-org delete
    """
    token: str
    comments: Optional[str] = None
    reason: Optional[OrganisationDeleteReason] = None


class UserOrganisationSummary(BaseModel):
    id: int
    name: Optional[str] = None
    onboarding_state: OnboardingState
    address: Optional[Address] = None
    prefer_self_host: Optional[bool] = None
    is_admin: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class UserUISettingsModel(BaseModel):
    preferred_currency: Optional[Currency] = None
    current_org_id: Optional[int] = None
    last_git_org_id: Optional[str] = None
    last_git_platform: Optional[PlatformEnum] = None
    page_size: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    """
    User in a particular organisation
    """
    id: int
    name: str
    avatar_url: Optional[str] = None
    email: str
    is_active: bool
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    id: int
    name: str
    avatar_url: Optional[str] = None
    token: uuid.UUID
    email: str
    uisettings: UserUISettingsModel
    account: Optional[AccountDetails] = None
    is_pending: bool
    is_staff: Optional[bool] = False
    organisations: list[UserOrganisationSummary]
    model_config = ConfigDict(from_attributes=True)


class UserInvite(BaseModel):
    email: str
    is_admin: Optional[bool] = None


class UserEmail(BaseModel):
    email: str


class UserUpdate(BaseModel):
    is_admin: bool


class APIToken(BaseModel):
    id: int
    token: uuid.UUID
    created: datetime
    model_config = ConfigDict(from_attributes=True)


class OAuthCodeResponse(BaseModel):
    code: str
    organisation_id: Optional[int] = None
    orgtoken: Optional[str] = None


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
    file: Optional[str] = None  # TODO make this required
    line: int
    column: int
    frame: str
    language: str


class TestResultError(BaseModel):
    title: str
    type: Optional[str] = None
    test_line: Optional[int] = None
    message: str
    stack: str
    code_frame: Optional[CodeFrame] = None
    video: Optional[str] = None


class TestResult(BaseModel):
    title: str
    context: str
    status: TestResultStatus
    retry: int = 0
    duration: Optional[float] = None
    failure_screenshots: Optional[list[str]] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[TestResultError] = None


class SpecResult(BaseModel):
    tests: List[TestResult]
    video: Optional[str] = None
    timeout: Optional[bool] = False


class ResultSummary(BaseModel):
    total: int = 0
    skipped: int = 0
    passes: int = 0
    failures: int = 0


class BaseProject(BaseModel):
    repos: str = Field(description="Repository name")
    platform: PlatformEnum = Field(description="Git platform")
    organisation_id: int = Field(description="Owner organisation ID")
    default_branch: str = Field(description="Default branch")
    url: str = Field(description="URL to git repository")
    owner: Optional[str] = None


class NewProject(BaseProject):
    name: str = Field(description="Project name e.g Git repository name")

    framework: AppFramework = AppFramework.generic
    parallelism: int = Field(description="Number of runner pods i.e the parallelism of the runner job",
                             default=4, ge=0, le=30)
    checks_integration: bool = True

    agent_id: Optional[int] = Field(None, description="ID of the agent that should be used to run this test. "
                                                "Only required for self-hosted agents")

    browser: str

    spec_deadline: Optional[int] = Field(
        description="Deadline in seconds to assign to an individual spec. If 0 then there will be no deadline set "
                    "(although the runner deadline still applies)",
        default=0,
        le=3600)
    spec_filter: Optional[str] = Field(None, description="Only test specs matching this regex")

    max_failures: Optional[int] = Field(None, description="Maximum number of failed test allowed before we quit and mark the"
                                        " run as failed")

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
        None, description="Docker image used for both build and run steps. Can only be specified for self-hosted agents")

    public_image_id: Optional[int] = Field(None, description="ID of the public Cykubed image used, if any")

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
    model_config = ConfigDict(from_attributes=True)


class Project(NewProject):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UpdatedProject(NewProject):
    id: int
    model_config = ConfigDict(from_attributes=True)


class NewRunnerImage(BaseModel):
    tag: str = Field(description="Docker image tag")
    image: str = Field(description="Docker image (without the tag)")
    node_version: str = Field(description="Node major version")
    description: Optional[str] = Field(None, description="Description")
    chrome: Optional[bool] = Field(description="True if this image contains Chrome", default=True)
    firefox: Optional[bool] = Field(description="True if this image contains Firefox", default=False)
    edge: Optional[bool] = Field(description="True if this image contains Edge", default=False)
    model_config = ConfigDict(from_attributes=True)


class RunnerImage(NewRunnerImage):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Workspace(BaseModel):
    slug: str
    name: str


class GitOrganisation(BaseModel):
    id: int
    name: str
    platform_id: Optional[str] = None
    login: str
    model_config = ConfigDict(from_attributes=True)


class Repository(BaseModel):
    id: str | int
    owner: Optional[str] = None
    name: str
    url: str
    platform: PlatformEnum
    default_branch: Optional[str] = None
    pushed_at: Optional[datetime] = None
    git_organisation: Optional[GitOrganisation] = None
    user_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class PendingAuthorisation(BaseModel):
    platform: PlatformEnum
    redirect_uri: Optional[str] = None


class AppInstallationState(BaseModel):
    installed: bool


class TestRunSpec(BaseModel):
    id: int
    file: str
    model_config = ConfigDict(from_attributes=True)


class TestRunStatusUpdate(BaseModel):
    status: TestRunStatus


class BaseTestRun(BaseModel):
    id: int
    local_id: int
    branch: str
    sha: Optional[str] = None
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
    preprovision: Optional[bool] = None
    status: Optional[TestRunStatus] = None
    model_config = ConfigDict(from_attributes=True)


class CacheItem(BaseModel):
    organisation_id: int
    name: str
    ttl: int  # TTL in secs
    storage_size: int  # Size in GB
    expires: datetime  # expiry date
    specs: Optional[list[str]] = None


class TestRunUpdate(BaseModel):
    started: datetime
    finished: Optional[datetime] = None
    status: TestRunStatus


class SpecFile(BaseModel):
    file: str
    status: Optional[SpecFileStatus] = None
    pod_name: Optional[str] = None
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    termination_count: Optional[int] = 0
    duration: Optional[int] = None
    failures: int = 0
    result: Optional[SpecResult] = None
    model_config = ConfigDict(from_attributes=True)


class SpecFileName(BaseModel):
    file: str


class SpecFileLog(BaseModel):
    file: str
    log: str
    model_config = ConfigDict(from_attributes=True)


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
    avatar_url: Optional[AnyHttpUrl] = None
    model_config = ConfigDict(from_attributes=True)


class CommitDetailsModel(BaseModel):
    author: AuthorModel
    message: str
    commit_url: str
    model_config = ConfigDict(from_attributes=True)


class TestRunCommon(BaseTestRun):
    status: TestRunStatus
    fixed: Optional[bool] = None
    error: Optional[str] = None
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    commit: Optional[CommitDetailsModel] = None
    duration: Optional[int] = None
    total_tests: Optional[int] = None
    failed_tests: Optional[int] = None
    flakey_tests: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class TestRunSummary(TestRunCommon):
    project_id: int
    project_name: str
    model_config = ConfigDict(from_attributes=True)


class TestRunSummaries(PaginatedModel):
    items: list[TestRunSummary]


class TestRunErrorReport(BaseModel):
    stage: str
    msg: str
    error_code: Optional[int] = None


#
# Webhooks
#


class CommonTriggerModel(BaseModel):
    organisation_id: int
    project_id: Optional[int] = None
    name: Optional[str] = None
    on_pass: Optional[bool] = False
    on_fail: Optional[bool] = False
    on_fixed: Optional[bool] = False
    on_flake: Optional[bool] = False
    branch_regex: Optional[str] = None

    @model_validator(mode='before')
    def check_triggers(cls, values):
        if type(values) is dict:
            if (not values.get('on_pass') and not values.get('on_fail') and not values.get('on_flake') and
                    not values.get('on_fixed')):
                raise ValueError('Specify at least one trigger')
        return values


class NewWebHook(CommonTriggerModel):
    url: str


class WebHook(NewWebHook):
    id: int
    project_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class WebhookHistory(BaseModel):
    hook_id: int
    testrun_id: int
    created: datetime
    status_code: Optional[int] = None
    request: str
    response: Optional[str] = None
    error: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


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
    project_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


#
# TestRun detail
#

class TestRunJobStats(BaseModel):
    total_build_seconds: Optional[int] = None
    total_runner_seconds: Optional[int] = None

    total_cpu_seconds: Optional[int] = None
    total_memory_gb_seconds: Optional[int] = None
    total_ephemeral_gb_seconds: Optional[int] = None

    cpu_seconds_normal: Optional[int] = None
    memory_gb_seconds_normal: Optional[int] = None
    ephemeral_gb_seconds_normal: Optional[int] = None

    cpu_seconds_spot: Optional[int] = None
    memory_gb_seconds_spot: Optional[int] = None
    ephemeral_gb_seconds_spot: Optional[int] = None

    total_cost_usd: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class KubernetesPlatformPricingModel(BaseModel):
    platform: KubernetesPlatform
    updated: datetime
    region: str
    cpu_spot_price: Optional[float] = None
    cpu_normal_price: Optional[float] = None
    memory_spot_price: Optional[float] = None
    memory_normal_price: Optional[float] = None
    ephemeral_price: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class TestRunDetail(TestRunCommon):
    project: Project
    files: Optional[list[SpecFile]] = None
    jobstats: Optional[TestRunJobStats] = None

    @field_validator('files', mode="before")
    @classmethod
    def _iter_to_list(cls, v):
        """
        It's not entirely obvious why I need this, as according to the docs this should serialize fine.
        However, without this Pydantic will complain as v isn't a list
        :param v:
        :return:
        """
        return list(v or [])
    model_config = ConfigDict(from_attributes=True)


class NewAgentModel(BaseModel):
    organisation_id: int


class UpdatedAgentModel(SpotEnabledModel):
    name: Optional[str] = 'A'
    platform: Optional[KubernetesPlatform] = KubernetesPlatform.generic
    replicated: Optional[bool] = False
    namespace: Optional[str] = None
    storage_class: Optional[str] = None
    platform_project_id: Optional[str] = None
    preprovision: Optional[bool] = None

    service_account: Optional[str] = None
    is_public: Optional[bool] = None


class AgentModel(UpdatedAgentModel, NewAgentModel):
    id: int
    token: uuid.UUID
    name: str
    storage_class: Optional[str] = None
    namespace: Optional[str] = None
    organisation_id: int
    organisation_name: Optional[str] = None
    first_connected: Optional[datetime] = None
    version: Optional[str] = None
    connected: int = 0
    is_public: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class AgentListModel(BaseModel):
    agents: list[AgentModel]
    latest_version: str


class NotificationChannel(BaseModel):
    id: str
    public: Optional[bool] = None
    name: str


class NotificationChannels(BaseModel):
    channels: list[NotificationChannel]


class TestRunJobStatus(BaseModel):
    name: str
    status: str
    message: Optional[str] = None


class PodStatus(BaseModel):
    pod_name: str
    project_id: int
    testrun_id: int
    phase: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_spot: bool
    duration: Optional[float] = None
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


class ExceededIncludeBuildCredits(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.exceeded_build_credits


class SpecFileMessage(BaseAppSocketMessage):
    testrun_id: int
    spec: SpecFile


class WebhookNotifiedMessage(BaseAppSocketMessage):
    action: AppWebSocketActions = AppWebSocketActions.webhook_notified
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
    host: Optional[str] = None
    step: Optional[int] = None

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
    duration: float
    terminated: bool = False


class AgentSpecCompleted(BaseModel):
    file: str
    finished: datetime
    result: SpecResult


class AgentSpecStarted(BaseModel):
    file: str
    pod_name: Optional[str] = None
    started: datetime


#
# Agent websocket
#

class AgentEvent(BaseModel):
    type: AgentEventType
    duration: Optional[float] = None
    testrun_id: int
    error_code: Optional[int] = None


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

####


class AdminDateTime(BaseModel):
    dt: Optional[datetime] = None
