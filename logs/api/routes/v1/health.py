from fastapi import APIRouter

from core.settings import settings
from schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["logs-health"])


@router.get("", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(service=settings.APP_NAME)
