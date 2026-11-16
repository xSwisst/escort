from __future__ import annotations

from aiogram import Dispatcher
from fastapi import FastAPI

from api import create_api_app
from bot.handlers import get_routers
from core.settings import settings
from services.bot import bot
from services.thread_manager import thread_manager
from shared.server.webhook import create_webhook_app


def create_app() -> FastAPI:
    dispatcher = Dispatcher()
    for router in get_routers():
        dispatcher.include_router(router)

    return create_webhook_app(
        bot=bot,
        dispatcher=dispatcher,
        api_factory=create_api_app,
        webhook_url=settings.WEBHOOK_URL,
        webhook_secret=settings.WEBHOOK_SECRET_TOKEN,
        allowed_updates=["message", "callback_query"],
        on_startup=[thread_manager.initialize],
    )


app = create_app()
