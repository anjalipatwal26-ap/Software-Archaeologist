from pydantic import BaseModel


class DependencyItem(BaseModel):
    module: str
    path: str | None = None


class FileDependencyResponse(BaseModel):
    status: str
    file: str
    dependencies: list[DependencyItem]
    message: str | None = None


class DirectoryDependencyResponse(BaseModel):
    status: str
    files: list[FileDependencyResponse]

class DependencyNode(BaseModel):
    id: str
    label: str


class DependencyEdge(BaseModel):
    source: str
    target: str

class DependencyGraphResponse(BaseModel):
    status: str
    nodes: list[DependencyNode]
    edges: list[DependencyEdge]