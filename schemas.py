from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator

from .enums import PlatformEnum, TestRunStatus, TestResultStatus


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
    platform: PlatformEnum


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

    class Config:
        orm_mode = True


class TestRunSummary(NewTestRun):
    started: datetime
    finished: Optional[datetime] = None
    total_files: int
    completed_files: int
    status: TestRunStatus
    active: bool
    progress_percentage: int

    class Config:
        orm_mode = True


class TestRunDetail(TestRunSummary):
    files: list[SpecFile] = []

    @validator('files', pre=True)
    def _iter_to_list(cls, v):
        return list(v)

    class Config:
        orm_mode = True



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


class Results(BaseModel):
    testrun_id: int
    specs: List[SpecResult]
    total: int = 0
    skipped: int = 0
    passes: int = 0
    failures: int = 0
