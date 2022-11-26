from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from .enums import PlatformEnum, Status, TestResultStatus


class UserProfile(BaseModel):
    name: str
    avatar_url: Optional[str]
    token: str
    email: str
    integrations: list[str]
    hub_token: str
    organisation_id: int
    organisation_name: str


class OrganisationIn(BaseModel):
    name: str


class Project(BaseModel):
    id: int
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


class Repository(BaseModel):
    id: str
    name: str
    url: str
    owner: str
    platform: PlatformEnum


class NewTestRun(BaseModel):
    id: int
    project: Project
    branch: str
    sha: str


class TestRunUpdate(BaseModel):
    started: datetime
    finished: Optional[datetime] = None

    status: Status


class SpecFile(BaseModel):
    file: str
    started: Optional[datetime] = None
    finished: Optional[datetime] = None


class TestRun(NewTestRun):
    started: datetime
    finished: Optional[datetime] = None
    active: bool
    status: Status
    files: List[SpecFile] = []
    remaining: List[SpecFile] = []

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
    video: Optional[str]


class TestResult(BaseModel):
    title: str
    status: TestResultStatus
    retry: int = 0
    duration: Optional[int]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error: Optional[TestResultError]
    manual_screenshots: Optional[List[str]]


class SpecResult(BaseModel):
    file: str
    tests: List[TestResult]


class Results(BaseModel):
    testrun_id: int
    specs: List[SpecResult]
    total: int = 0
    skipped: int = 0
    passes: int = 0
    failures: int = 0
