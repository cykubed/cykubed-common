from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from enums import PlatformEnum, Status


class OrganisationIn(BaseModel):
    name: str


class NewProject(BaseModel):
    name: str
    repository: str
    url: str
    slug: Optional[str]
    workspace: Optional[str]
    platform: PlatformEnum


class Repository(BaseModel):
    name: str
    slug: str
    url: str
    workspace: Optional[str]
    platform: PlatformEnum


class NewTestRun(BaseModel):
    id: int
    project_id: int
    branch: str
    sha: str


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


class CodeFrame(BaseModel):
    line: int
    column: int
    file: str
    frame: str


class TestResultError(BaseModel):
    name: str
    message: str
    stack: str
    code_frame: CodeFrame
    screenshots: List[str]
    videos: List[str]


class TestResult(BaseModel):
    title: str
    failed: bool
    body: str
    num_attempts: int
    duration: Optional[int]; display_error: Optional[str]
    started_at: Optional[datetime]
    error: Optional[TestResultError]


class SpecResult(BaseModel):
    file: str
    results: List[TestResult]


class Results(BaseModel):
    testrun_id: int
    specs: List[SpecResult]
    total: int = 0
    skipped: int = 0
    passes: int = 0
    failures: int = 0
