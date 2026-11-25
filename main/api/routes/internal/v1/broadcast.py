from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from repository.repositories.clients import ClientRepository
from shared.bot.session import resolve_session

router = APIRouter(prefix="/internal/v1", tags=["internal-broadcast"])
logger = logging.getLogger(__name__)


class BroadcastButton(BaseModel):
    text: str
    url: str


class BroadcastRequest(BaseModel):
    admin_id: int
    audience: str = "all"
    text: str
    media_url: str | None = None
    buttons: list[BroadcastButton] = Field(default_factory=list)


def _build_markup(buttons: list[BroadcastButton]) -> InlineKeyboardMarkup | None:
    if not buttons:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=b.text, url=b.url)] for b in buttons if b.text and b.url]
    )


@router.post("/broadcast")
async def send_broadcast(payload: BroadcastRequest, request: Request):
    bot: Bot | None = getattr(request.app.state, "bot", None)
    if not bot:
        logger.error("Bot instance not found on app.state")
        return {"ok": False, "sent": 0, "failed": 0, "total": 0, "total_queued": 0, "success": False}

    async with resolve_session() as session:
        clients_repo = ClientRepository(session)
        user_ids = await clients_repo.get_broadcast_recipients(payload.admin_id, audience=payload.audience)

    markup = _build_markup(payload.buttons)
    sent = 0
    failed = 0
    total = len(user_ids)

    for user_id in user_ids:
        try:
            if payload.media_url:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=payload.media_url,
                    caption=payload.text,
                    reply_markup=markup,
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=payload.text,
                    reply_markup=markup,
                )
            sent += 1
        except Exception as exc:
            logger.debug("Broadcast send failed for user_id=%s: %s", user_id, exc)
            failed += 1
        await asyncio.sleep(0.04)

    return {
        "ok": True,
        "sent": sent,
        "failed": failed,
        "total": total,
        "total_queued": total,
        "success": True,
    }
