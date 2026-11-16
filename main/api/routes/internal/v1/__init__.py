from fastapi import APIRouter

from .notify import router as notify_router

router = APIRouter()
router.include_router(notify_router)

__all__ = ["router"]
