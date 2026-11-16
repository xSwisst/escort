from aiogram import Router

from .address import router as address_router
from .info import router as info_router
from .models import router as models_router
from .profile import router as profile_router
from .search_with_code import router as search_with_code_router
from .start import router as start_router
from .support import router as support_router


def get_routers() -> list[Router]:
    return [
        start_router,
        info_router,
        support_router,
        models_router,
        search_with_code_router,
        profile_router,
        address_router,
    ]


__all__ = ["get_routers"]
