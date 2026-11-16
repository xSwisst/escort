"""
Отправка логов в Telegram форум-топики через aiogram с поддержкой медиагрупп.
"""
from __future__ import annotations

import base64
import logging
from typing import Sequence

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import httpx

from core.settings import settings
from schemas import LogEventRequest
from ..bot import bot
from ..event_mapping import get_thread_type_for_event
from ..formatter import format_event_message
from ..history import client_log_history
from ..thread_manager import thread_manager

logger = logging.getLogger(__name__)

PHOTOS_INTERNAL_URL = "http://photos:8005"

CHECK_EVENT_TYPES = {
    "get_check_of_top_up",
    "get_check_of_payment_private_channel",
    "get_check_of_payment_model",
}


def _build_invoice_action_markup(invoice_number: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"log:inv:appr:{invoice_number}",
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"log:inv:rej:{invoice_number}",
                ),
            ]
        ]
    )


async def _fetch_photo_bytes(storage_key: str) -> bytes | None:
    if not storage_key:
        return None
    cleaned = storage_key.strip()
    urls_to_try = []
    if "/c/" in cleaned:
        path = cleaned.split("/c/", 1)[1]
        urls_to_try.append(f"{PHOTOS_INTERNAL_URL}/c/{path}")
    elif cleaned.startswith("http://") or cleaned.startswith("https://"):
        urls_to_try.append(cleaned)
    else:
        urls_to_try.append(f"{PHOTOS_INTERNAL_URL}/c/{cleaned.lstrip('/')}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in urls_to_try:
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and resp.content:
                    return resp.content
            except Exception:
                continue
    return None


async def _extract_media_bytes(payload: dict) -> list[bytes]:
    result: list[bytes] = []

    # 1. Base64 photos
    photos_b64 = payload.get("photos_b64") or []
    if isinstance(photos_b64, str):
        photos_b64 = [photos_b64]
    for b64_str in photos_b64:
        try:
            result.append(base64.b64decode(b64_str))
        except Exception:
            pass

    single_b64 = payload.get("photo_b64")
    if single_b64 and isinstance(single_b64, str):
        try:
            result.append(base64.b64decode(single_b64))
        except Exception:
            pass

    # 2. Storage keys or URLs
    photos_keys = payload.get("photos") or []
    if isinstance(photos_keys, str):
        photos_keys = [photos_keys]
    for key in photos_keys:
        if isinstance(key, str) and key.strip():
            b = await _fetch_photo_bytes(key)
            if b:
                result.append(b)

    single_key = payload.get("photo")
    if single_key and isinstance(single_key, str) and single_key.strip():
        b = await _fetch_photo_bytes(single_key)
        if b:
            result.append(b)

    return result


class TelegramLogSender:
    """Форматирует событие и отправляет в соответствующий тред форума."""

    async def _send_to_thread(
        self,
        thread_id: int,
        text: str,
        media_bytes: list[bytes],
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        """Отправка сообщения или медиагруппы в конкретный тред."""
        if not media_bytes:
            await bot.send_message(
                chat_id=settings.LOGS_CHAT_ID,
                message_thread_id=thread_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            return

        has_short_caption = len(text) <= 1024
        caption_text = text if has_short_caption else None

        if len(media_bytes) == 1:
            await bot.send_photo(
                chat_id=settings.LOGS_CHAT_ID,
                message_thread_id=thread_id,
                photo=BufferedInputFile(media_bytes[0], filename="photo.jpg"),
                caption=caption_text,
                parse_mode="HTML" if caption_text else None,
                reply_markup=reply_markup if has_short_caption else None,
            )
        else:
            media_group: list[InputMediaPhoto] = []
            for i, b in enumerate(media_bytes[:10]):
                media_group.append(
                    InputMediaPhoto(
                        media=BufferedInputFile(b, filename=f"photo_{i}.jpg"),
                        caption=caption_text if i == 0 else None,
                        parse_mode="HTML" if (i == 0 and caption_text) else None,
                    )
                )
            await bot.send_media_group(
                chat_id=settings.LOGS_CHAT_ID,
                message_thread_id=thread_id,
                media=media_group,
            )

        # Если текст длиннее 1024 символов или если была медиагруппа с кнопками, отправляем отдельным сообщением
        if not has_short_caption and text:
            await bot.send_message(
                chat_id=settings.LOGS_CHAT_ID,
                message_thread_id=thread_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        elif len(media_bytes) > 1 and reply_markup:
            await bot.send_message(
                chat_id=settings.LOGS_CHAT_ID,
                message_thread_id=thread_id,
                text="Действие с чеком:",
                reply_markup=reply_markup,
            )

    async def send(self, event: LogEventRequest) -> bool:
        """Отправить событие в Telegram."""
        thread_type = get_thread_type_for_event(event.event_type)
        thread_id = await thread_manager.ensure_thread(thread_type)

        if thread_id is None:
            logger.error(
                "Cannot send log: no thread for event_type='%s' (thread_type='%s')",
                event.event_type,
                thread_type,
            )
            return False

        log_id = await client_log_history.record_activity(event)

        text = await format_event_message(event, log_id=log_id)
        if not text:
            logger.debug("Skipping event '%s' - no template configured", event.event_type)
            return True

        payload = event.payload or {}
        media_bytes = await _extract_media_bytes(payload)

        reply_markup = None
        if event.event_type in CHECK_EVENT_TYPES:
            invoice_num = (
                payload.get("invoice_number")
                or payload.get("order_number")
                or payload.get("order_id")
            )
            if invoice_num:
                reply_markup = _build_invoice_action_markup(str(invoice_num))

        try:
            await self._send_to_thread(thread_id, text, media_bytes, reply_markup=reply_markup)
            return True
        except TelegramBadRequest as exc:
            if "thread not found" in str(exc).lower():
                logger.warning(
                    "Thread %d for '%s' not found (deleted). Recreating and retrying...",
                    thread_id,
                    thread_type,
                )
                new_thread_id = await thread_manager.recreate_thread(thread_type)
                if new_thread_id is not None:
                    try:
                        await self._send_to_thread(new_thread_id, text, media_bytes, reply_markup=reply_markup)
                        return True
                    except Exception:
                        logger.exception(
                            "Failed to send log to newly recreated thread %d (event_type='%s')",
                            new_thread_id,
                            event.event_type,
                        )
                        return False
            logger.exception("Failed to send log to Telegram (event_type='%s')", event.event_type)
            return False
        except Exception:
            logger.exception("Failed to send log to Telegram (event_type='%s')", event.event_type)
            return False


telegram_log_sender = TelegramLogSender()
