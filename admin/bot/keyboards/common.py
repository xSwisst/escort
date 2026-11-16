from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from shared.bot.keyboards.pagination import build_pagination_row


def back_btn(cb: str = "admin:panel") -> InlineKeyboardButton:
    return InlineKeyboardButton(**btn("back", callback_data=cb))


def back_ikb(cb: str = "admin:panel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn(cb)]])


def kb_back(callback_data: str) -> InlineKeyboardMarkup:
    return back_ikb(callback_data)


def nav_buttons(page: int, total_pages: int, prefix: str) -> list[InlineKeyboardButton]:
    if total_pages <= 1:
        return []
    return build_pagination_row(page, total_pages, prefix)

