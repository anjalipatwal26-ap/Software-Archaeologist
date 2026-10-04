
import subprocess
from pathlib import Path
from uuid import uuid4

from git import Repo


CLONE_BASE_DIR = Path("data/repositories")


def clone_repository(repository_url: str) -> dict:
    repository_id = uuid4().hex

    repository_path = CLONE_BASE_DIR / repository_id

    repository_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        Repo.clone_from(
            repository_url,
            repository_path,
        )

        return {
            "status": "success",
            "repository_url": repository_url,
            "local_path": str(repository_path),
        }

    except Exception as error:
        return {
            "status": "error",
            "repository_url": repository_url,
            "local_path": None,
            "message": str(error),
        }


def analyze_commit(commit) -> dict:
    changed_files = []

    if commit.parents:
        parent = commit.parents[0]

        diff_items = parent.diff(
            commit,
        )

    else:
        repository = commit.repo

        result = subprocess.run(
            [
                "git",
                "-C",
                str(repository.working_tree_dir),
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--name-status",
                "-r",
                commit.hexsha,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.splitlines():
            parts = line.split("\t")

            if len(parts) >= 2:
                changed_files.append(
                    {
                        "file": parts[-1],
                        "change_type": parts[0][0],
                    }
                )

        return {
            "sha": commit.hexsha,
            "message": commit.message.strip(),
            "author": commit.author.name,
            "email": commit.author.email,
            "date": commit.committed_datetime.isoformat(),
            "changed_files": changed_files,
            "insertions": 0,
            "deletions": 0,
            "files_changed": len(changed_files),
            "parents": [
                parent.hexsha
                for parent in commit.parents
            ],
        }

    for diff in diff_items:
        if diff.new_file:
            change_type = "A"

        elif diff.deleted_file:
            change_type = "D"

        elif diff.renamed_file:
            change_type = "R"

        else:
            change_type = "M"

        changed_files.append(
            {
                "file": diff.b_path or diff.a_path,
                "change_type": change_type,
            }
        )

    return {
        "sha": commit.hexsha,
        "message": commit.message.strip(),
        "author": commit.author.name,
        "email": commit.author.email,
        "date": commit.committed_datetime.isoformat(),
        "changed_files": changed_files,
        "insertions": commit.stats.total["insertions"],
        "deletions": commit.stats.total["deletions"],
        "files_changed": commit.stats.total["files"],
        "parents": [
            parent.hexsha
            for parent in commit.parents
        ],
    }


def get_commit_diff(commit) -> list[dict]:
    diffs = []

    if commit.parents:
        parent = commit.parents[0]

        diff_items = parent.diff(
            commit,
            create_patch=True,
        )

        for diff in diff_items:
            patch = diff.diff

            if isinstance(patch, bytes):
                patch = patch.decode(
                    "utf-8",
                    errors="ignore",
                )

            if diff.new_file:
                change_type = "A"

            elif diff.deleted_file:
                change_type = "D"

            elif diff.renamed_file:
                change_type = "R"

            else:
                change_type = "M"

            diffs.append(
                {
                    "file": diff.b_path or diff.a_path,
                    "change_type": change_type,
                    "diff": patch,
                }
            )

    else:
        repository = commit.repo

        result = subprocess.run(
            [
                "git",
                "-C",
                str(repository.working_tree_dir),
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--patch",
                "-r",
                commit.hexsha,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        current_file = None
        current_patch = []

        for line in result.stdout.splitlines():
            if line.startswith("diff --git "):

                if current_file is not None:
                    diffs.append(
                        {
                            "file": current_file,
                            "change_type": "A",
                            "diff": "\n".join(
                                current_patch
                            ),
                        }
                    )

                parts = line.split(" ", 3)

                if len(parts) >= 4:
                    current_file = parts[3].replace("b/", "", 1)

                current_patch = [line]

            elif current_file is not None:
                current_patch.append(line)

        if current_file is not None:
            diffs.append(
                {
                    "file": current_file,
                    "change_type": "A",
                    "diff": "\n".join(
                        current_patch
                    ),
                }
            )

    return diffs


def get_commit_history(
    repository_path: str,
    limit: int = 20,
) -> list[dict]:
    repository = Repo(repository_path)

    commits = []

    for commit in repository.iter_commits(
        max_count=limit
    ):
        commits.append(
            analyze_commit(commit)
        )

    return commits

