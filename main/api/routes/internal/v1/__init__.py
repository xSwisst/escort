from fastapi import APIRouter

from .bot_meta import router as bot_meta_router
from .broadcast import router as broadcast_router
from .notify import router as notify_router

router = APIRouter()
router.include_router(notify_router)
router.include_router(bot_meta_router)
router.include_router(broadcast_router)

__all__ = ["router"]
