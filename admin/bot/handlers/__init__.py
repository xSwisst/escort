from aiogram import Router

from .agreements import router as agreements_router
from .cards import router as cards_router
from .client_logs import router as client_logs_router
from .clients import router as clients_router
from .forms import router as forms_router
from .malling import router as malling_router
from .panel import router as panel_router
from .promos import router as promos_router
from .start import router as start_router


def get_routers() -> list[Router]:
    return [
        start_router,
        panel_router,
        forms_router,
        client_logs_router,
        clients_router,
        promos_router,
        agreements_router,
        cards_router,
        malling_router,
    ]


__all__ = ["get_routers"]
