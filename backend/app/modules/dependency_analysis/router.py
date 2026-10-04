from fastapi import APIRouter, Query

from app.modules.dependency_analysis.service import (
    analyze_file_dependencies,
    analyze_directory_dependencies,
    build_dependency_graph,
    build_directory_dependency_graph,
)


router = APIRouter(
    prefix="/dependency-analysis",
    tags=["Dependency Analysis"],
)


# ---------------------------------------------------------
# Analyze a single file
# ---------------------------------------------------------

@router.get("")
def analyze_file(
    file_path: str = Query(...),
    project_root: str = Query("."),
):
    return analyze_file_dependencies(
        file_path=file_path,
        project_root=project_root,
    )


# ---------------------------------------------------------
# Analyze all Python files in a directory
# ---------------------------------------------------------

@router.get("/directory")
def analyze_directory(
    directory_path: str = Query(...),
    project_root: str = Query("."),
):
    results = analyze_directory_dependencies(
        directory_path=directory_path,
        project_root=project_root,
    )

    return {
        "status": "success",
        "files": results,
    }


# ---------------------------------------------------------
# Build dependency graph for a single file
# ---------------------------------------------------------

@router.get("/graph")
def dependency_graph(
    file_path: str = Query(...),
    project_root: str = Query("."),
):
    return build_dependency_graph(
        file_path=file_path,
        project_root=project_root,
    )


# ---------------------------------------------------------
# Build dependency graph for an entire repository
# ---------------------------------------------------------

@router.get("/graph/directory")
def directory_dependency_graph(
    directory_path: str = Query(...),
    project_root: str = Query("."),
):
    return build_directory_dependency_graph(
        directory_path=directory_path,
        project_root=project_root,
    )