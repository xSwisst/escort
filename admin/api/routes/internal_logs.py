from __future__ import annotations

import base64
import logging

from aiogram import Bot
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from clients.api import api_client

router = APIRouter(prefix="/internal/v1/notify", tags=["admin-internal-notify"])
logger = logging.getLogger(__name__)


class ClientLogNotifyRequest(BaseModel):
    admin_telegram_id: int
    client_user_id: int
    event_type: str
    text: str
    photos_b64: list[str] = Field(default_factory=list)


def _client_log_markup(client_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Открыть клиента",
                    callback_data=f"admin:user:{client_user_id}",
                )
            ]
        ]
    )


@router.post("/client-log")
async def notify_worker_client_log(payload: ClientLogNotifyRequest, request: Request) -> dict:
    if not await api_client.admin.is_client_log_enabled(payload.admin_telegram_id, payload.event_type):
        return {"ok": True, "skipped": "disabled"}

    bot: Bot | None = getattr(request.app.state, "bot", None)
    if bot is None:
        logger.error("admin-bot instance not found on app.state")
        return {"ok": False, "error": "bot_not_found"}

    markup = _client_log_markup(payload.client_user_id)
    media_bytes: list[bytes] = []
    for raw_b64 in payload.photos_b64[:10]:
        try:
            decoded = base64.b64decode(raw_b64)
            if decoded:
                media_bytes.append(decoded)
        except Exception:
            continue

    try:
        if not media_bytes:
            await bot.send_message(
                chat_id=payload.admin_telegram_id,
                text=payload.text,
                parse_mode="HTML",
                reply_markup=markup,
            )
        elif len(media_bytes) == 1:
            short_caption = len(payload.text) <= 1024
            await bot.send_photo(
                chat_id=payload.admin_telegram_id,
                photo=BufferedInputFile(media_bytes[0], filename="log.jpg"),
                caption=payload.text if short_caption else None,
                parse_mode="HTML" if short_caption else None,
                reply_markup=markup if short_caption else None,
            )
            if not short_caption:
                await bot.send_message(
                    chat_id=payload.admin_telegram_id,
                    text=payload.text,
                    parse_mode="HTML",
                    reply_markup=markup,
                )
        else:
            short_caption = len(payload.text) <= 1024
            group = [
                InputMediaPhoto(
                    media=BufferedInputFile(b, filename=f"log_{i}.jpg"),
                    caption=payload.text if (i == 0 and short_caption) else None,
                    parse_mode="HTML" if (i == 0 and short_caption) else None,
                )
                for i, b in enumerate(media_bytes)
            ]
            await bot.send_media_group(chat_id=payload.admin_telegram_id, media=group)
            await bot.send_message(
                chat_id=payload.admin_telegram_id,
                text=payload.text if not short_caption else "Действие с клиентом:",
                parse_mode="HTML",
                reply_markup=markup,
            )
        return {"ok": True}
    except Exception as exc:
        logger.warning(
            "Failed to send client log DM to admin_telegram_id=%s event=%s: %s",
            payload.admin_telegram_id,
            payload.event_type,
            exc,
        )
        return {"ok": False, "error": str(exc)}
