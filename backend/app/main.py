
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.health.router import router as health_router
from app.modules.repository.router import router as repository_router
from app.modules.source_analysis.router import router as source_analysis_router
from app.modules.git_analysis.router import router as git_analysis_router
from app.modules.dependency_analysis.router import (
    router as dependency_analysis_router,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/api",
)

app.include_router(
    repository_router,
    prefix="/api",
)

app.include_router(
    source_analysis_router,
    prefix="/api",
)

app.include_router(
    git_analysis_router,
    prefix="/api",
)

app.include_router(
    dependency_analysis_router,
    prefix="/api",
)

