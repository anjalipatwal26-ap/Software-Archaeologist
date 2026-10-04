from fastapi import APIRouter, HTTPException

from git import Repo

from app.modules.git_analysis.service import (
    get_commit_diff,
    get_commit_history,
)


router = APIRouter()


@router.get("/git-analysis")
def git_analysis(
    repository_path: str,
    limit: int = 20,
):
    try:
        commits = get_commit_history(
            repository_path,
            limit,
        )

        return {
            "repository_path": repository_path,
            "commits_analyzed": len(commits),
            "commits": commits,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/git-analysis/commit/{commit_sha}/diff")
def commit_diff(
    repository_path: str,
    commit_sha: str,
):
    try:
        repository = Repo(repository_path)

        commit = repository.commit(commit_sha)

        diffs = get_commit_diff(commit)

        return {
            "commit": commit_sha,
            "message": commit.message.strip(),
            "files_with_diffs": len(diffs),
            "diffs": diffs,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )