from fastapi import APIRouter, HTTPException

from app.modules.repository.schemas import (
    RepositoryAnalyzeRequest,
    RepositoryAnalyzeResponse,
    RepositoryDetailResponse,
    RepositoryListItem,
)
from app.modules.repository.service import (
    analyze_repository,
    get_repositories,
    get_repository_by_id,
)


router = APIRouter()


@router.post(
    "/repositories/analyze",
    response_model=RepositoryAnalyzeResponse,
)
def analyze_repository_endpoint(
    request: RepositoryAnalyzeRequest,
):
    return analyze_repository(str(request.repository_url))


@router.get(
    "/repositories",
    response_model=list[RepositoryListItem],
)
def get_repositories_endpoint():
    return get_repositories()


@router.get(
    "/repositories/{repository_id}",
    response_model=RepositoryDetailResponse,
)
def get_repository_endpoint(repository_id: int):
    repository = get_repository_by_id(repository_id)

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found.",
        )

    return repository