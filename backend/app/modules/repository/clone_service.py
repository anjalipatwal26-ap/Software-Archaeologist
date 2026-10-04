from pathlib import Path
from urllib.parse import urlparse

from git import Repo
from git.exc import GitCommandError


BASE_DIR = Path(__file__).resolve().parents[3]

REPOSITORIES_DIR = (
    BASE_DIR / "storage" / "repositories"
)


def get_repository_name(repository_url: str) -> str:
    parsed_url = urlparse(repository_url)

    repository_name = (
        parsed_url.path
        .strip("/")
        .split("/")[-1]
    )

    if repository_name.endswith(".git"):
        repository_name = repository_name[:-4]

    return repository_name


def clone_repository(repository_url: str) -> dict:
    repository_name = get_repository_name(
        repository_url
    )

    if not repository_name:
        return {
            "status": "error",
            "message": "Invalid repository URL.",
        }

    repository_path = (
        REPOSITORIES_DIR / repository_name
    )

    try:
        REPOSITORIES_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if repository_path.exists():
            return {
                "status": "exists",
                "message": "Repository already exists.",
                "repository_name": repository_name,
                "repository_path": str(
                    repository_path
                ),
            }

        Repo.clone_from(
            repository_url,
            repository_path,
        )

        return {
            "status": "success",
            "message": "Repository cloned successfully.",
            "repository_name": repository_name,
            "repository_path": str(
                repository_path
            ),
        }

    except GitCommandError as error:
        return {
            "status": "error",
            "message": "Failed to clone repository.",
            "details": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "message": (
                "Unexpected error while cloning repository."
            ),
            "details": str(error),
        }