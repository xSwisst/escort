from fastapi import APIRouter

from .about import router as about_router
from .auth import router as auth_router
from .bookings import router as bookings_router
from .favorites import router as favorites_router
from .models import router as models_router
from .profile import router as profile_router
from .support import router as support_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(about_router)
router.include_router(support_router)
router.include_router(models_router)
router.include_router(favorites_router)
router.include_router(bookings_router)
router.include_router(profile_router)

__all__ = ["router"]
