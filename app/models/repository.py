from pydantic import BaseModel, HttpUrl


class RepositoryRequest(BaseModel):
    github_url: HttpUrl


class FileRepresentation(BaseModel):
    path: str
    language: str | None = None
    size: int
    important: bool = False
    content: str | None = None


class RepositoryRepresentation(BaseModel):
    name: str
    full_name: str
    description: str | None = None
    default_branch: str
    language: str | None = None
    files: list[FileRepresentation]