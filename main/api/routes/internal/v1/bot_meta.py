from __future__ import annotations

import logging

from aiogram import Bot
from fastapi import APIRouter, Request

router = APIRouter(prefix="/internal/v1", tags=["internal-meta"])
logger = logging.getLogger(__name__)


@router.get("/bot-info")
async def get_bot_info(request: Request):
    bot: Bot | None = getattr(request.app.state, "bot", None)
    if not bot:
        return {"is_alive": False, "username": None, "full_name": None}

    cached = getattr(request.app.state, "_bot_me", None)
    if cached is None:
        try:
            me = await bot.get_me()
            cached = {
                "is_alive": True,
                "username": me.username,
                "full_name": me.full_name,
            }
            request.app.state._bot_me = cached
        except Exception as exc:
            logger.warning("Failed to fetch bot.get_me(): %s", exc)
            return {"is_alive": False, "username": None, "full_name": None}
    return cached
