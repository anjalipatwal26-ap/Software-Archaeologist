from datetime import datetime

import httpx

from app.core.database import SessionLocal
from app.models.repository import Branch, Commit, Contributor, Repository
from app.modules.repository.clone_service import clone_repository


GITHUB_API_BASE_URL = "https://api.github.com"


def parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def save_repository_data(
    data: dict,
    commits: list[dict],
    contributors: list[dict],
    branches: list[dict],
) -> None:
    db = SessionLocal()

    try:
        repository = (
            db.query(Repository)
            .filter(Repository.github_id == data["id"])
            .first()
        )

        if repository is None:
            repository = Repository(
                github_id=data["id"],
                owner=data["owner"]["login"],
                name=data["name"],
                full_name=data["full_name"],
                url=data["html_url"],
                description=data.get("description"),
                language=data.get("language"),
                stars=data.get("stargazers_count", 0),
                forks=data.get("forks_count", 0),
                open_issues=data.get("open_issues_count", 0),
                default_branch=data["default_branch"],
                github_created_at=parse_github_datetime(
                    data.get("created_at")
                ),
                github_updated_at=parse_github_datetime(
                    data.get("updated_at")
                ),
            )

            db.add(repository)
            db.flush()

        else:
            repository.owner = data["owner"]["login"]
            repository.name = data["name"]
            repository.full_name = data["full_name"]
            repository.url = data["html_url"]
            repository.description = data.get("description")
            repository.language = data.get("language")
            repository.stars = data.get("stargazers_count", 0)
            repository.forks = data.get("forks_count", 0)
            repository.open_issues = data.get(
                "open_issues_count", 0
            )
            repository.default_branch = data["default_branch"]

            repository.github_created_at = (
                parse_github_datetime(
                    data.get("created_at")
                )
            )

            repository.github_updated_at = (
                parse_github_datetime(
                    data.get("updated_at")
                )
            )

        # ---------------------------------------------------------
        # Save commits
        # ---------------------------------------------------------

        existing_shas = {
            sha
            for sha, in (
                db.query(Commit.sha)
                .filter(
                    Commit.repository_id == repository.id
                )
                .all()
            )
        }

        for commit_data in commits:

            if commit_data["sha"] in existing_shas:
                continue

            commit = Commit(
                repository_id=repository.id,
                sha=commit_data["sha"],
                message=commit_data["message"],
                author=commit_data["author"],
                authored_at=parse_github_datetime(
                    commit_data["date"]
                ),
            )

            db.add(commit)

        # ---------------------------------------------------------
        # Save contributors
        # ---------------------------------------------------------

        existing_contributors = {
            contributor.username: contributor
            for contributor in (
                db.query(Contributor)
                .filter(
                    Contributor.repository_id
                    == repository.id
                )
                .all()
            )
            if contributor.username
        }

        for contributor_data in contributors:

            username = contributor_data["username"]

            if not username:
                continue

            contributor = existing_contributors.get(
                username
            )

            if contributor is None:

                contributor = Contributor(
                    repository_id=repository.id,
                    github_id=contributor_data["github_id"],
                    username=username,
                    display_name=contributor_data[
                        "display_name"
                    ],
                    contributions=contributor_data[
                        "contributions"
                    ],
                    avatar_url=contributor_data[
                        "avatar_url"
                    ],
                )

                db.add(contributor)

            else:

                contributor.github_id = contributor_data[
                    "github_id"
                ]

                contributor.display_name = contributor_data[
                    "display_name"
                ]

                contributor.contributions = contributor_data[
                    "contributions"
                ]

                contributor.avatar_url = contributor_data[
                    "avatar_url"
                ]

        # ---------------------------------------------------------
        # Save branches
        # ---------------------------------------------------------

        existing_branches = {
            branch.name: branch
            for branch in (
                db.query(Branch)
                .filter(
                    Branch.repository_id == repository.id
                )
                .all()
            )
        }

        for branch_data in branches:

            branch_name = branch_data["name"]

            if not branch_name:
                continue

            branch = existing_branches.get(
                branch_name
            )

            if branch is None:

                branch = Branch(
                    repository_id=repository.id,
                    name=branch_name,
                    sha=branch_data["sha"],
                    protected=branch_data["protected"],
                )

                db.add(branch)

            else:

                branch.sha = branch_data["sha"]
                branch.protected = branch_data[
                    "protected"
                ]

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def analyze_repository(repository_url: str) -> dict:

    # ---------------------------------------------------------
    # Validate GitHub URL
    # ---------------------------------------------------------

    parts = [
        part
        for part in repository_url.rstrip("/").split("/")
        if part
    ]

    if (
        len(parts) < 2
        or "github.com" not in repository_url
    ):
        return {
            "repository_url": repository_url,
            "status": "invalid",
            "message": (
                "Please provide a valid GitHub repository URL."
            ),
            "repository_path": None,
            "commits": [],
            "branches": [],
        }

    owner = parts[-2]

    repository = parts[-1].removesuffix(".git")

    # ---------------------------------------------------------
    # Clone repository locally
    # ---------------------------------------------------------

    clone_result = clone_repository(repository_url)

    print("CLONE RESULT:", clone_result)

    if clone_result["status"] == "error":

        return {
            "repository_url": repository_url,
            "status": "error",
            "message": clone_result["message"],
            "repository_path": None,
            "commits": [],
            "branches": [],
        }

    repository_path = clone_result.get(
        "repository_path"
    )

    # ---------------------------------------------------------
    # GitHub API URLs
    # ---------------------------------------------------------

    repository_api_url = (
        f"{GITHUB_API_BASE_URL}/repos/"
        f"{owner}/{repository}"
    )

    commits_api_url = (
        f"{GITHUB_API_BASE_URL}/repos/"
        f"{owner}/{repository}/commits"
    )

    branches_api_url = (
        f"{GITHUB_API_BASE_URL}/repos/"
        f"{owner}/{repository}/branches"
    )

    contributors_api_url = (
        f"{GITHUB_API_BASE_URL}/repos/"
        f"{owner}/{repository}/contributors"
    )

    headers = {
        "Accept": "application/vnd.github+json"
    }

    # ---------------------------------------------------------
    # Get repository information
    # ---------------------------------------------------------

    try:

        repository_response = httpx.get(
            repository_api_url,
            timeout=10.0,
            headers=headers,
        )

        if repository_response.status_code == 404:

            return {
                "repository_url": repository_url,
                "status": "not_found",
                "message": (
                    "GitHub repository was not found."
                ),
                "repository_path": repository_path,
                "commits": [],
                "branches": [],
            }

        repository_response.raise_for_status()

        data = repository_response.json()

        # -----------------------------------------------------
        # Get commits
        # -----------------------------------------------------

        commits_response = httpx.get(
            commits_api_url,
            params={"per_page": 10},
            timeout=10.0,
            headers=headers,
        )

        commits_response.raise_for_status()

        commits_data = commits_response.json()

        commits = []

        for commit in commits_data:

            commit_details = commit.get(
                "commit", {}
            )

            author_details = (
                commit_details.get("author")
                or {}
            )

            commits.append(
                {
                    "sha": commit.get("sha"),
                    "message": commit_details.get(
                        "message", ""
                    ),
                    "author": author_details.get(
                        "name"
                    ),
                    "date": author_details.get(
                        "date"
                    ),
                }
            )

        # -----------------------------------------------------
        # Get branches
        # -----------------------------------------------------

        branches_response = httpx.get(
            branches_api_url,
            params={"per_page": 100},
            timeout=10.0,
            headers=headers,
        )

        branches_response.raise_for_status()

        branches_data = branches_response.json()

        branches = []

        for branch in branches_data:

            branches.append(
                {
                    "name": branch.get("name"),
                    "sha": branch.get(
                        "commit", {}
                    ).get("sha"),
                    "protected": branch.get(
                        "protected", False
                    ),
                }
            )

        # -----------------------------------------------------
        # Get contributors
        # -----------------------------------------------------

        contributors_response = httpx.get(
            contributors_api_url,
            params={"per_page": 100},
            timeout=10.0,
            headers=headers,
        )

        contributors_response.raise_for_status()

        contributors_data = (
            contributors_response.json()
        )

        contributors = []

        for contributor in contributors_data:

            contributors.append(
                {
                    "github_id": contributor.get(
                        "id"
                    ),
                    "username": contributor.get(
                        "login"
                    ),
                    "display_name": contributor.get(
                        "name"
                    ),
                    "contributions": contributor.get(
                        "contributions", 0
                    ),
                    "avatar_url": contributor.get(
                        "avatar_url"
                    ),
                }
            )

        # -----------------------------------------------------
        # Save data to database
        # -----------------------------------------------------

        save_repository_data(
            data,
            commits,
            contributors,
            branches,
        )

        # -----------------------------------------------------
        # Final response
        # -----------------------------------------------------

        return {
            "repository_url": repository_url,
            "status": "valid",
            "message": (
                f"Repository found: "
                f"{data['full_name']}"
            ),

            # IMPORTANT
            # This is the local cloned repository path.
            "repository_path": repository_path,

            "name": data.get("name"),

            "owner": data.get(
                "owner", {}
            ).get("login"),

            "description": data.get(
                "description"
            ),

            "language": data.get(
                "language"
            ),

            "stars": data.get(
                "stargazers_count"
            ),

            "forks": data.get(
                "forks_count"
            ),

            "open_issues": data.get(
                "open_issues_count"
            ),

            "default_branch": data.get(
                "default_branch"
            ),

            "created_at": data.get(
                "created_at"
            ),

            "updated_at": data.get(
                "updated_at"
            ),

            "commits": commits,

            "branches": branches,
        }

    except httpx.HTTPError:

        return {
            "repository_url": repository_url,
            "status": "error",
            "message": (
                "Could not connect to GitHub."
            ),
            "repository_path": repository_path,
            "commits": [],
            "branches": [],
        }


def get_repositories() -> list[Repository]:

    db = SessionLocal()

    try:

        return (
            db.query(Repository)
            .all()
        )

    finally:

        db.close()


def get_repository_by_id(
    repository_id: int,
) -> dict | None:

    db = SessionLocal()

    try:

        repository = (
            db.query(Repository)
            .filter(
                Repository.id == repository_id
            )
            .first()
        )

        if repository is None:
            return None

        commits = (
            db.query(Commit)
            .filter(
                Commit.repository_id
                == repository.id
            )
            .order_by(
                Commit.authored_at.desc()
            )
            .all()
        )

        branches = (
            db.query(Branch)
            .filter(
                Branch.repository_id
                == repository.id
            )
            .all()
        )

        contributors = (
            db.query(Contributor)
            .filter(
                Contributor.repository_id
                == repository.id
            )
            .all()
        )

        return {
            "id": repository.id,
            "owner": repository.owner,
            "name": repository.name,
            "full_name": repository.full_name,
            "url": repository.url,
            "description": repository.description,
            "language": repository.language,
            "stars": repository.stars,
            "forks": repository.forks,
            "open_issues": repository.open_issues,
            "default_branch": repository.default_branch,
            "ingested_at": repository.ingested_at,

            "commits": [
                {
                    "sha": commit.sha,
                    "message": commit.message,
                    "author": commit.author,
                    "date": commit.authored_at,
                }
                for commit in commits
            ],

            "branches": [
                {
                    "name": branch.name,
                    "sha": branch.sha,
                    "protected": branch.protected,
                }
                for branch in branches
            ],

            "contributors": [
                {
                    "github_id": contributor.github_id,
                    "username": contributor.username,
                    "display_name": contributor.display_name,
                    "contributions": contributor.contributions,
                    "avatar_url": contributor.avatar_url,
                }
                for contributor in contributors
            ],
        }

    finally:

        db.close()