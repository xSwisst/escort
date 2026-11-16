from aiogram import Router

from .answer import router as answer_router
from .info import router as info_router
from .moderation import router as moderation_router
from .question import router as question_router
from .start import router as start_router


def get_routers() -> list[Router]:
    return [
        start_router,
        info_router,
        moderation_router,
        answer_router,
        question_router,
    ]


__all__ = ["get_routers"]
