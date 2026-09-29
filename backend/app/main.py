from fastapi import FastAPI

from app.core.config import settings
from app.modules.health.router import router as health_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(
    health_router,
    prefix="/api",
)