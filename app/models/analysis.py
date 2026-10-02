from pydantic import BaseModel


class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    description: str | None
    default_branch: str
    language: str | None


class Summary(BaseModel):
    overview: str
    architecture: str
    main_components: list[str]
    technologies: list[str]
    entry_points: list[str]


class Architecture(BaseModel):
    entry_points: list[str]
    components: list[str]
    relationships: list[str]
    data_flow: list[str]


class AnalysisResponse(BaseModel):
    repository: RepositoryInfo
    summary: Summary
    architecture: Architecture