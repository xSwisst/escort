from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from shared.bot.keyboards import build_pagination_row


def main_reply_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    del is_admin
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn("main_menu_reply")["text"])]],
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
