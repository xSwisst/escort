from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from shared.bot.keyboards import build_pagination_row


def reply_btn(key: str, default_text: str | None = None) -> KeyboardButton:
    data = btn(key)
    text = data.get("text", default_text or key)
    kwargs: dict[str, str] = {"text": text}
    emoji_id = data.get("icon_custom_emoji_id")
    if emoji_id:
        kwargs["icon_custom_emoji_id"] = str(emoji_id)
    return KeyboardButton(**kwargs)


def main_reply_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    del is_admin
    return ReplyKeyboardMarkup(
        keyboard=[
            [reply_btn("reply_models", "Модели")],
            [reply_btn("reply_profile", "Профиль"), reply_btn("reply_search_code", "Поиск по коду")],
            [reply_btn("reply_information", "Информация (о нас)")],
        ],
        resize_keyboard=True,
    )


def premium_btn(text_key: str, callback_data: str, *, url: str | None = None) -> InlineKeyboardButton:
    if url:
        return InlineKeyboardButton(**btn(text_key, url=url))
    return InlineKeyboardButton(**btn(text_key, callback_data=callback_data))


def back_btn(text_key: str = "back_to_main", callback_data: str = "menu:main") -> InlineKeyboardButton:
    return InlineKeyboardButton(**btn(text_key, callback_data=callback_data))


def kb_back(text_key: str = "back_to_main", callback_data: str = "menu:main") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(back_btn(text_key, callback_data))
    return builder.as_markup()





def nav_buttons(page: int, total_pages: int, prefix: str) -> list[InlineKeyboardButton]:
    if total_pages <= 1:
        return []
    return build_pagination_row(page, total_pages, prefix)
