from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator

from .enums import PlatformEnum, TestRunStatus, TestResultStatus, AppWebSocketActions


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
    screenshot: Optional[str]
    video: Optional[str]


class TestResult(BaseModel):
    title: str
    context: str
    status: TestResultStatus
    retry: int = 0
    duration: Optional[int]
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


class UserProfile(BaseModel):
    name: str
    avatar_url: Optional[str]
    token: str
    email: str
    integrations: list[str]
    hub_token: Optional[str]
    organisation_id:  int
    organisation_name: str


class NewProject(BaseModel):
    name: str
    slug: Optional[str]
    workspace: Optional[str]
    platform: PlatformEnum
    url: str
    parallelism: int
    build_cmd = 'ng build --output-path=dist'
    server_cmd = 'ng serve'
    server_port: int = 4200
    # TODO add reporting


class Project(NewProject):
    id: int

    class Config:
        orm_mode = True


class Repository(BaseModel):
    id: str
    name: str
    url: str
    owner: str
    owner_avatar_url: Optional[str]
    pushed_at: Optional[datetime]
    platform: PlatformEnum


class TestRunSpec(BaseModel):
    id: int
    file: str

    class Config:
        orm_mode = True


class TestRunSpecs(BaseModel):
    """
    Sent by the hub to update the list of specs and the SHA
    """
    sha: str
    specs: list[str]

    class Config:
        orm_mode = True


class TestRunStatusUpdate(BaseModel):
    status: TestRunStatus


class NewTestRun(BaseModel):
    """
    Sent to the hub to kick off a run
    """
    id: int
    project: Project
    branch: str
    sha: Optional[str]

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


class CommitDetailsModel(BaseModel):
    author_email: str
    author_name: str
    author_avatar_url: Optional[str]
    message: str
    commit_url: str


class TestRunCommon(NewTestRun):
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


class HubStateMessage(BaseAppSocketMessage):
    hubstate: HubStateModel


class TestRunUpdateMessage(BaseAppSocketMessage):
    testrun: TestRunSummary


class TestRunSpecUpdateMessage(BaseAppSocketMessage):
    testrun_id: int
    status: TestRunStatus
    file: SpecFile


class LogUpdateMessage(BaseAppSocketMessage):
    testrun_id: int
    position: int
    log: str

