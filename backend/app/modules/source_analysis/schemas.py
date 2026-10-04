from pydantic import BaseModel, Field


class FunctionInfo(BaseModel):
    name: str
    line: int


class MethodInfo(BaseModel):
    name: str
    line: int


class ClassInfo(BaseModel):
    name: str
    line: int
    methods: list[MethodInfo] = Field(default_factory=list)


class SourceAnalysisResponse(BaseModel):
    status: str
    file: str
    imports: list[str] = Field(default_factory=list)
    functions: list[FunctionInfo] = Field(default_factory=list)
    classes: list[ClassInfo] = Field(default_factory=list)
    message: str | None = None

class DirectoryAnalysisResponse(BaseModel):
    directory: str
    files_analyzed: int
    files: list[SourceAnalysisResponse] = Field(
        default_factory=list
    )