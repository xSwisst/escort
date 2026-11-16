from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn


def kb_back(callback_data: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("back", callback_data=callback_data)))
    return builder.as_markup()
