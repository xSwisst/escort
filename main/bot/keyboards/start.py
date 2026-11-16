from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn


def kb_accept_agreement(
    url: str | None = None,
    name: str | None = None,
    action: str | None = None,
    action_arg: str | None = None,
):
    del name
    builder = InlineKeyboardBuilder()
    if url:
        builder.row(InlineKeyboardButton(**btn("read_agreement", url=url)))
    callback_data = f"start:accept:{action}:{action_arg}" if action and action_arg else "start:accept"
    builder.row(InlineKeyboardButton(**btn("acquainted", callback_data=callback_data)))
    return builder.as_markup()
