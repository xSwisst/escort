from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, InputMediaPhoto, LinkPreviewOptions

from shared.bot.utils.cache import cache_message_media, get_cached, get_cached_kind, get_media_path
from shared.bot.utils.media_common import build_photo_media, caption_value, is_message_not_modified

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import InlineKeyboardMarkup, Message


def _resolve_parse_mode(bot: "Bot", parse_mode: str | None) -> str | None:
    if parse_mode is not None:
        return parse_mode
    default = getattr(bot, "default", None)
    return getattr(default, "parse_mode", "HTML") or "HTML"



def _has_media(message: "Message") -> bool:
    return bool(message.photo)


async def _send_message(
    message: "Message",
    *,
    text: str | None = None,
    reply_markup: "InlineKeyboardMarkup | None" = None,
    banner: str | None = None,
    parse_mode: str | None = None,
    link_preview_options: LinkPreviewOptions | None = None,
) -> "Message":
    effective_parse_mode = _resolve_parse_mode(message.bot, parse_mode)
    if not banner:
        kwargs: dict[str, Any] = {"text": text or "\u2063", "reply_markup": reply_markup}
        if effective_parse_mode is not None:
            kwargs["parse_mode"] = effective_parse_mode
        if link_preview_options is not None:
            kwargs["link_preview_options"] = link_preview_options
        return await message.answer(**kwargs)

    file_id = await get_cached(banner)
    kind = get_cached_kind(banner)
    caption = caption_value(text)
    if file_id and kind:
        return await message.answer_photo(photo=file_id, caption=caption, reply_markup=reply_markup, parse_mode=effective_parse_mode)

    path = get_media_path(banner)
    if path is None or kind is None:
        kwargs = {"text": text or "\u2063", "reply_markup": reply_markup}
        if effective_parse_mode is not None:
            kwargs["parse_mode"] = effective_parse_mode
        return await message.answer(**kwargs)

    sent = await message.answer_photo(photo=FSInputFile(path=str(path)), caption=caption, reply_markup=reply_markup, parse_mode=effective_parse_mode)
    cache_message_media(banner, sent)
    return sent


async def send_message(message: "Message", **kwargs: Any) -> "Message":
    return await _send_message(message, **kwargs)


async def replace_message(message: "Message", **kwargs: Any) -> "Message":
    try:
        await message.delete()
    except Exception:
        pass
    return await _send_message(message, **kwargs)


async def edit_message(
    message: "Message",
    *,
    text: str | None = None,
    reply_markup: "InlineKeyboardMarkup | None" = None,
    banner: str | None = None,
    allow_replace: bool = True,
    parse_mode: str | None = None,
    link_preview_options: LinkPreviewOptions | None = None,
) -> "Message | bool":
    effective_parse_mode = _resolve_parse_mode(message.bot, parse_mode)
    caption = caption_value(text)
    try:
        if not banner:
            if _has_media(message):
                return await message.edit_caption(caption=caption, reply_markup=reply_markup, parse_mode=effective_parse_mode)
            kwargs: dict[str, Any] = {"text": text or "\u2063", "reply_markup": reply_markup}
            if effective_parse_mode is not None:
                kwargs["parse_mode"] = effective_parse_mode
            if link_preview_options is not None:
                kwargs["link_preview_options"] = link_preview_options
            return await message.edit_text(**kwargs)

        file_id = await get_cached(banner)
        kind = get_cached_kind(banner)
        if not kind:
            return await message.edit_text(text or "\u2063", reply_markup=reply_markup, parse_mode=effective_parse_mode)
        if file_id:
            return await message.edit_media(media=build_photo_media(file_id, caption, effective_parse_mode), reply_markup=reply_markup)
        path = get_media_path(banner)
        if path is None:
            return await message.edit_text(text or "\u2063", reply_markup=reply_markup, parse_mode=effective_parse_mode)
        result = await message.edit_media(
            media=build_photo_media(FSInputFile(path=str(path)), caption, effective_parse_mode),
            reply_markup=reply_markup,
        )
        cache_message_media(banner, result)
        return result
    except TelegramBadRequest as exc:
        if is_message_not_modified(exc):
            return True
    if allow_replace:
        return await replace_message(message, text=text, reply_markup=reply_markup, banner=banner, parse_mode=parse_mode, link_preview_options=link_preview_options)
    raise
