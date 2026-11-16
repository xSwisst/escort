from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile

from shared.bot.utils.actions import edit_message as shared_edit_message
from shared.bot.utils.actions import send_message as shared_send_message
from shared.bot.utils.cache import cache_message_media, get_cached, get_cached_kind, get_media_path
from shared.bot.utils.media_common import build_photo_media, caption_value, is_message_not_modified

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import InlineKeyboardMarkup, Message

async def answer_banner(message: "Message", text: str, *, banner: str, reply_markup: "InlineKeyboardMarkup | None" = None):
    return await shared_send_message(message, text=text, reply_markup=reply_markup, banner=banner)


async def edit_banner(message: "Message", text: str, *, banner: str, reply_markup: "InlineKeyboardMarkup | None" = None):
    return await shared_edit_message(message, text=text, reply_markup=reply_markup, banner=banner)


async def bot_send_banner(
    bot: "Bot",
    chat_id: int,
    text: str,
    *,
    banner: str,
    reply_markup: "InlineKeyboardMarkup | None" = None,
):
    caption = caption_value(text)
    file_id = await get_cached(banner)
    if file_id and get_cached_kind(banner) == "photo":
        return await bot.send_photo(chat_id=chat_id, photo=file_id, caption=caption, reply_markup=reply_markup)
    path = get_media_path(banner)
    if path is None:
        return await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    sent = await bot.send_photo(chat_id=chat_id, photo=FSInputFile(path=str(path)), caption=caption, reply_markup=reply_markup)
    cache_message_media(banner, sent)
    return sent


async def bot_edit_banner(
    bot: "Bot",
    chat_id: int,
    message_id: int,
    text: str,
    *,
    banner: str,
    reply_markup: "InlineKeyboardMarkup | None" = None,
):
    caption = caption_value(text)
    try:
        file_id = await get_cached(banner)
        if file_id:
            media = build_photo_media(file_id, caption)
        else:
            path = get_media_path(banner)
            if path is None:
                raise FileNotFoundError(banner)
            media = build_photo_media(FSInputFile(path=str(path)), caption)
        result = await bot.edit_message_media(chat_id=chat_id, message_id=message_id, media=media, reply_markup=reply_markup)
        cache_message_media(banner, result)
        return result
    except TelegramBadRequest as exc:
        if is_message_not_modified(exc):
            return True
        try:
            await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, reply_markup=reply_markup)
            return True
        except TelegramBadRequest as exc2:
            if is_message_not_modified(exc2):
                return True
    except Exception:
        pass

    try:
        await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, reply_markup=reply_markup)
        return True
    except TelegramBadRequest as exc:
        if is_message_not_modified(exc):
            return True
    except Exception:
        pass
    return None


async def answer_photo(
    message: "Message",
    text: str,
    photo: str,
    *,
    reply_markup: "InlineKeyboardMarkup | None" = None,
):
    caption = caption_value(text)
    return await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup)


async def bot_send_photo(
    bot: "Bot",
    chat_id: int,
    text: str,
    photo: str,
    *,
    reply_markup: "InlineKeyboardMarkup | None" = None,
):
    caption = caption_value(text)
    return await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup)


async def bot_edit_photo(
    bot: "Bot",
    chat_id: int,
    message_id: int,
    text: str,
    photo: str,
    *,
    reply_markup: "InlineKeyboardMarkup | None" = None,
):
    caption = caption_value(text)
    try:
        return await bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=build_photo_media(photo, caption),
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as exc:
        if is_message_not_modified(exc):
            return True
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    return await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup)
