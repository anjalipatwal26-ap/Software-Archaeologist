import ast
from pathlib import Path


def analyze_file_dependencies(
    file_path: str,
    project_root: str = ".",
) -> dict:

    path = Path(file_path)

    if not path.exists():
        return {
            "status": "not_found",
            "file": str(path),
            "dependencies": [],
        }

    if not path.is_file():
        return {
            "status": "error",
            "file": str(path),
            "dependencies": [],
            "message": "Path is not a file",
        }

    try:
        source_code = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(source_code)

        dependencies = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:

                    module_name = alias.name

                    resolved_path = module_to_file_path(
                        module_name,
                        project_root,
                    )

                    dependencies.append(
                        {
                            "module": module_name,
                            "path": resolved_path,
                        }
                    )

            elif isinstance(node, ast.ImportFrom):

                if not node.module:
                    continue

                module_name = node.module

                if node.level > 0:

                    current_file = Path(file_path)

                    relative_base = current_file.parent

                    for _ in range(node.level - 1):
                        relative_base = relative_base.parent

                    relative_module_path = (
                        relative_base
                        / module_name.replace(".", "/")
                    )

                    python_file = (
                        relative_module_path.with_suffix(".py")
                    )

                    init_file = (
                        relative_module_path
                        / "__init__.py"
                    )

                    if python_file.exists():
                        resolved_path = str(python_file)

                    elif init_file.exists():
                        resolved_path = str(init_file)

                    else:
                        resolved_path = None

                else:

                    resolved_path = module_to_file_path(
                        module_name,
                        project_root,
                    )

                dependencies.append(
                    {
                        "module": module_name,
                        "path": resolved_path,
                    }
                )

        return {
            "status": "success",
            "file": str(path),
            "dependencies": dependencies,
        }

    except SyntaxError as error:

        return {
            "status": "syntax_error",
            "file": str(path),
            "dependencies": [],
            "message": str(error),
        }

    except Exception as error:

        return {
            "status": "error",
            "file": str(path),
            "dependencies": [],
            "message": str(error),
        }

def analyze_directory_dependencies(
    directory_path: str,
    project_root: str | None = None,
) -> list[dict]:

    directory = Path(directory_path)

    if not directory.exists() or not directory.is_dir():
        return []

    # If project_root is not supplied,
    # use the directory itself.
    if project_root is None:
        project_root = str(directory)

    results = []

    for file_path in directory.rglob("*.py"):

        # Ignore virtual environments
        if ".venv" in file_path.parts:
            continue

        # Ignore Git internals
        if ".git" in file_path.parts:
            continue

        results.append(
            analyze_file_dependencies(
                str(file_path),
                project_root,
            )
        )

    return results


def module_to_file_path(
    module_name: str,
    project_root: str,
) -> str | None:

    root = Path(project_root)

    module_parts = module_name.split(".")

    module_path = root.joinpath(
        *module_parts
    )

    python_file = module_path.with_suffix(".py")

    if python_file.exists():
        return str(python_file)

    init_file = module_path / "__init__.py"

    if init_file.exists():
        return str(init_file)

    # Support repositories using a src/ directory.
    src_root = root / "src"

    if src_root.exists():

        src_module_path = src_root.joinpath(
            *module_parts
        )

        src_python_file = (
            src_module_path.with_suffix(".py")
        )

        if src_python_file.exists():
            return str(src_python_file)

        src_init_file = (
            src_module_path / "__init__.py"
        )

        if src_init_file.exists():
            return str(src_init_file)

    return None

    


def build_dependency_graph(
    file_path: str,
    project_root: str = ".",
) -> dict:

    analysis = analyze_file_dependencies(
        file_path,
        project_root,
    )

    if analysis["status"] != "success":

        return {
            "status": analysis["status"],
            "nodes": [],
            "edges": [],
        }

    nodes = []
    edges = []

    source_file = str(
        Path(file_path)
    ).replace("\\", "/")

    nodes.append(
        {
            "id": source_file,
            "label": source_file,
        }
    )

    for dependency in analysis["dependencies"]:

        dependency_path = dependency["path"]

        if dependency_path is None:
            continue

        dependency_file = str(
            Path(dependency_path)
        ).replace("\\", "/")

        nodes.append(
            {
                "id": dependency_file,
                "label": dependency_file,
            }
        )

        edges.append(
            {
                "source": source_file,
                "target": dependency_file,
            }
        )

    # ---------------------------------------------------------
    # Remove duplicate nodes
    # ---------------------------------------------------------

    unique_nodes = {
        node["id"]: node
        for node in nodes
    }

    # ---------------------------------------------------------
    # Remove duplicate edges
    # ---------------------------------------------------------

    unique_edges = {
        (
            edge["source"],
            edge["target"],
        ): edge
        for edge in edges
    }

    return {
        "status": "success",
        "nodes": list(
            unique_nodes.values()
        ),
        "edges": list(
            unique_edges.values()
        ),
    }


def build_directory_dependency_graph(
    directory_path: str,
    project_root: str | None = None,
) -> dict:

    directory = Path(directory_path)

    if not directory.exists() or not directory.is_dir():

        return {
            "status": "not_found",
            "nodes": [],
            "edges": [],
        }

    # ---------------------------------------------------------
    # Project root
    # ---------------------------------------------------------

    if project_root is None:
        project_root = str(directory)

    project_root_path = Path(project_root)

    nodes = []
    edges = []

    # ---------------------------------------------------------
    # Analyze every Python file
    # ---------------------------------------------------------

    for file_path in directory.rglob("*.py"):

        # Ignore virtual environment
        if ".venv" in file_path.parts:
            continue

        # Ignore Git internals
        if ".git" in file_path.parts:
            continue

        source_file = str(
            file_path
        ).replace("\\", "/")

        analysis = analyze_file_dependencies(
            source_file,
            project_root,
        )

        if analysis["status"] != "success":
            continue

        # -----------------------------------------------------
        # Add source node
        # -----------------------------------------------------

        nodes.append(
            {
                "id": source_file,
                "label": source_file,
            }
        )

        # -----------------------------------------------------
        # Add dependency nodes and edges
        # -----------------------------------------------------

        for dependency in analysis["dependencies"]:

            dependency_path = dependency["path"]

            if dependency_path is None:
                continue

            dependency_file = str(
                Path(dependency_path)
            ).replace("\\", "/")

            # -------------------------------------------------
            # Important:
            #
            # Only show dependencies that belong to
            # the analyzed repository.
            #
            # External libraries such as:
            #
            # import os
            # import json
            # import requests
            #
            # are ignored if they cannot be resolved
            # inside the repository.
            # -------------------------------------------------

            try:

                Path(
                    dependency_file
                ).resolve().relative_to(
                    project_root_path.resolve()
                )

            except ValueError:

                continue

            nodes.append(
                {
                    "id": dependency_file,
                    "label": dependency_file,
                }
            )

            edges.append(
                {
                    "source": source_file,
                    "target": dependency_file,
                }
            )

    # ---------------------------------------------------------
    # Remove duplicate nodes
    # ---------------------------------------------------------

    unique_nodes = {
        node["id"]: node
        for node in nodes
    }

    # ---------------------------------------------------------
    # Remove duplicate edges
    # ---------------------------------------------------------

    unique_edges = {
        (
            edge["source"],
            edge["target"],
        ): edge
        for edge in edges
    }

    return {
        "status": "success",
        "nodes": list(
            unique_nodes.values()
        ),
        "edges": list(
            unique_edges.values()
        ),
    }