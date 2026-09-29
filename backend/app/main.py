from fastapi import FastAPI

from app.core.config import settings
from app.modules.health.router import router as health_router
from app.modules.repository.router import router as repository_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(
    health_router,
    prefix="/api",
)

app.include_router(
    repository_router,
    prefix="/api",
)