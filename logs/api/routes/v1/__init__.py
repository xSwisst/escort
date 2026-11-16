from fastapi import APIRouter

from .events import router as events_router
from .health import router as health_router

router = APIRouter(prefix="/v1", tags=["logs-v1"])
router.include_router(events_router)
router.include_router(health_router)

__all__ = ["router"]
