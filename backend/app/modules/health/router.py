from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.modules.health.schemas import HealthResponse
from app.modules.health.service import check_database


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    database_connected = check_database()

    return HealthResponse(
        status="ok" if database_connected else "degraded",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        database="connected" if database_connected else "disconnected",
        timestamp=datetime.now(timezone.utc),
    )