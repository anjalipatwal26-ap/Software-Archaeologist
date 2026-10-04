from fastapi import APIRouter, HTTPException

from app.modules.source_analysis.schemas import (
    DirectoryAnalysisResponse,
    SourceAnalysisResponse,
)
from app.modules.source_analysis.service import (
    analyze_python_directory,
    analyze_python_file,
)


router = APIRouter()


@router.get(
    "/source-analysis",
    response_model=SourceAnalysisResponse,
)
def source_analysis(file_path: str):
    result = analyze_python_file(file_path)

    if result["status"] == "not_found":
        raise HTTPException(
            status_code=404,
            detail="Python file not found.",
        )

    return result


@router.get(
    "/source-analysis/directory",
    response_model=DirectoryAnalysisResponse,
)
def source_analysis_directory(directory_path: str):
    results = analyze_python_directory(directory_path)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Directory not found or contains no Python files.",
        )

    return {
        "directory": directory_path,
        "files_analyzed": len(results),
        "files": results,
    }