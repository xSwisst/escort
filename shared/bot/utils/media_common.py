from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto


def caption_value(text: str | None) -> str | None:
    if text is None:
        return None
    return text if text != "" else None


def is_message_not_modified(exc: TelegramBadRequest) -> bool:
    return "message is not modified" in str(exc).lower()


def build_photo_media(media, caption: str | None, parse_mode: str | None = "HTML") -> InputMediaPhoto:
    return InputMediaPhoto(media=media, caption=caption, parse_mode=parse_mode or "HTML")

