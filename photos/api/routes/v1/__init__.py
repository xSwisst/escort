from fastapi import APIRouter

from .files import router as files_router
from .health import router as health_router

router = APIRouter()
router.include_router(files_router)
router.include_router(health_router)

__all__ = ["router"]
