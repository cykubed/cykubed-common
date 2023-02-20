from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, validator

from .enums import PlatformEnum, TestRunStatus, TestResultStatus, AppWebSocketActions, LogLevel, AgentEventType


#
# Test results
#


class CodeFrame(BaseModel):
    line: int
    column: int
    frame: str
    language: str


class TestResultError(BaseModel):
    title: str
    type: str
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
    file: str
    tests: List[TestResult]
    video: Optional[str]


class ResultSummary(BaseModel):
    total: int = 0
    skipped: int = 0
    passes: int = 0
    failures: int = 0


class Results(ResultSummary):
    testrun_id: int
    specs: List[SpecResult]


class OrganisationIn(BaseModel):
    name: str


class OrganisationSummary(BaseModel):
    id: int
    name: str


class IntegrationSummary(BaseModel):
    name: PlatformEnum
    user_id: Optional[int]


class UserProfile(BaseModel):
    name: str
    avatar_url: Optional[str]
    token: str
    email: str
    integrations: list[IntegrationSummary]
    hub_token: Optional[str]
    organisation_id:  int
    organisation_name: str
    is_admin: bool
    integration_user_id: Optional[int]


class NewProject(BaseModel):
    name: str
    owner: Optional[str]
    default_branch: str
    platform: PlatformEnum
    url: str
    parallelism: int = 10
    build_cmd = 'ng build --output-path=dist'
    checks_integration: bool = True
    slack_channel_id: Optional[str]
    notify_on_passed: Optional[Union[bool, None]] = False

    build_cpu: str = '2'
    build_memory: str = '2G'
    build_deadline: int = 10*60

    runner_image: Optional[str]
    runner_cpu: str = '1'
    runner_memory: str = '2G'
    runner_deadline: int = 3600


class Project(NewProject):
    id: int
    organisation: OrganisationSummary

    class Config:
        orm_mode = True


class NewRunnerImage(BaseModel):
    node_version: str
    tag: str
    description: str
    chrome: bool
    firefox: bool
    edge: bool

    class Config:
        orm_mode = True


class RunnerImage(NewRunnerImage):
    id: int


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


class NewTestRun(BaseTestRun):
    """
    Sent to the agent to kick off a run
    """
    url: str
    cache_key: Optional[str]

    class Config:
        orm_mode = True


class TestRunUpdate(BaseModel):
    started: datetime
    finished: Optional[datetime] = None

    status: TestRunStatus


class SpecFile(BaseModel):
    file: str
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    failures: int = 0
    result: Optional[SpecResult]

    class Config:
        orm_mode = True


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

#
# TestRun detail
#


class TestRunDetail(TestRunCommon):
    files: Optional[list[SpecFile]]

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


class HubStateModel(BaseModel):
    first_connected: Optional[datetime]
    connected: bool

    class Config:
        orm_mode = True


class BaseAppSocketMessage(BaseModel):
    action: AppWebSocketActions

    def __str__(self):
        return f'{self.action} msg'


class HubStateMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.hub
    hubstate: HubStateModel


class TestRunDetailUpdateMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.testrun
    testrun: TestRunDetail


class AppLogMessage(BaseModel):
    source: str
    ts: datetime
    level: LogLevel
    msg: str
    step: Optional[int]

    def __str__(self):
        return self.msg


class SlackChannel(BaseModel):
    id: str
    name: str


class SlackChannels(BaseModel):
    next_cursor: Optional[str]
    channels: list[SlackChannel]


class CompletedBuild(BaseModel):
    """
    Completed build details
    """
    sha: str
    specs: list[str]
    cache_hash: str


class TestRunJobStatus(BaseModel):
    name: str
    status: str
    message: Optional[str]

#
# Agent websocket
#


class AgentEvent(BaseModel):
    type: AgentEventType
    testrun_id: int


class AgentCompletedBuildMessage(AgentEvent):
    build: CompletedBuild


class AgentSpecCompleted(AgentEvent):
    result: SpecResult


class AgentStatusChanged(AgentEvent):
    status: TestRunStatus


class AgentLogMessage(AgentEvent):
    msg: AppLogMessage


class LogUpdateMessage(BaseAppSocketMessage):
    action = AppWebSocketActions.buildlog
    testrun_id: int
    line_num: int
    msg: AppLogMessage


