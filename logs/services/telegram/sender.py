"""
Отправка логов в Telegram форум-топики через aiogram с поддержкой медиагрупп.
"""
from __future__ import annotations

import asyncio
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

WORKER_DM_EVENT_TYPES = {
    "new_user",
    "agreement_accepted",
    "add_city",
    "change_of_city",
    "add_address",
    "remove_address",
    "open_support_section",
    "message_to_support",
    "payment_request",
    "get_check_of_top_up",
    "get_check_of_payment_private_channel",
    "get_check_of_payment_model",
    "new_order",
    "open_model_form",
    "promocode_activated",
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
    if "/models/" in cleaned:
        path = cleaned.split("/models/", 1)[1]
        urls_to_try.append(f"{PHOTOS_INTERNAL_URL}/models/{path}")
    elif "/c/" in cleaned:
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

    async def _forward_to_admin_dm(
        self,
        *,
        admin_telegram_id: int,
        client_user_id: int,
        event_type: str,
        text: str,
        media_bytes: list[bytes],
    ) -> None:
        if not settings.ADMIN_BOT_URL:
            return
        url = f"{settings.ADMIN_BOT_URL.rstrip('/')}/internal/v1/notify/client-log"
        body = {
            "admin_telegram_id": int(admin_telegram_id),
            "client_user_id": int(client_user_id),
            "event_type": event_type,
            "text": text,
            "photos_b64": [base64.b64encode(b).decode("ascii") for b in media_bytes[:10]],
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=body)
                if resp.status_code != 200:
                    logger.warning("admin-bot client-log returned status=%s", resp.status_code)
        except Exception as exc:
            logger.warning("Failed to forward client log to admin-bot: %s", exc)

    async def send(self, event: LogEventRequest) -> bool:
        """Отправить событие в Telegram."""
        log_id = await client_log_history.record_activity(event)

        text = await format_event_message(event, log_id=log_id)
        if not text:
            logger.debug("Skipping event '%s' - no template configured", event.event_type)
            return True

        payload = event.payload or {}
        media_bytes = await _extract_media_bytes(payload)

        admin_tg_id = payload.get("admin_telegram_id")
        client_uid = payload.get("user_id") or payload.get("client_id") or event.actor_id
        if event.event_type in WORKER_DM_EVENT_TYPES and admin_tg_id and client_uid:
            try:
                asyncio.create_task(
                    self._forward_to_admin_dm(
                        admin_telegram_id=int(admin_tg_id),
                        client_user_id=int(client_uid),
                        event_type=event.event_type,
                        text=text,
                        media_bytes=media_bytes,
                    )
                )
            except Exception:
                pass

        thread_type = get_thread_type_for_event(event.event_type)
        thread_id = await thread_manager.ensure_thread(thread_type)

        if thread_id is None:
            logger.error(
                "Cannot send log: no thread for event_type='%s' (thread_type='%s')",
                event.event_type,
                thread_type,
            )
            return False

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
