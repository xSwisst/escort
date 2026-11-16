from fastapi import APIRouter

from core.settings import settings
from schemas import HealthResponse

router = APIRouter(tags=["photos-health"])


@router.get("/v1/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(service=settings.APP_NAME)
