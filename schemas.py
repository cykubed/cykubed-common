from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from models import PlatformEnum, TestRunStatus


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
    project_id: int
    branch: str
    sha: str


class TestRun(NewTestRun):
    started: datetime
    finished: Optional[datetime] = None
    status: TestRunStatus


class TestRunUpdate(BaseModel):
    started: datetime
    finished: Optional[datetime] = None
    status: TestRunStatus


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
