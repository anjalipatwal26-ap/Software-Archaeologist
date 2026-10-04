from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class RepositoryAnalyzeRequest(BaseModel):
    repository_url: HttpUrl


class CommitInfo(BaseModel):
    sha: str
    message: str
    author: str | None = None
    date: datetime | None = None

class BranchInfo(BaseModel):
    name: str
    sha: str
    protected: bool = False


class RepositoryAnalyzeResponse(BaseModel):
    repository_url: str
    status: str
    message: str
    repository_path: str | None = None

    name: str | None = None
    owner: str | None = None
    description: str | None = None
    language: str | None = None
    stars: int | None = None
    forks: int | None = None
    open_issues: int | None = None
    default_branch: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    commits: list[CommitInfo] = Field(default_factory=list)
    branches: list[BranchInfo] = Field(default_factory=list)

class RepositoryListItem(BaseModel):
    id: int
    owner: str
    name: str
    full_name: str
    url: str
    description: str | None = None
    language: str | None = None
    stars: int
    forks: int
    open_issues: int
    default_branch: str
    ingested_at: datetime

class ContributorInfo(BaseModel):
    github_id: int | None = None
    username: str | None = None
    display_name: str | None = None
    contributions: int = 0
    avatar_url: str | None = None

class RepositoryDetailResponse(BaseModel):
    id: int
    owner: str
    name: str
    full_name: str
    url: str
    description: str | None = None
    language: str | None = None
    stars: int
    forks: int
    open_issues: int
    default_branch: str
    ingested_at: datetime

    commits: list[CommitInfo] = Field(default_factory=list)
    branches: list[BranchInfo] = Field(default_factory=list)
    contributors: list[ContributorInfo] = Field(default_factory=list)