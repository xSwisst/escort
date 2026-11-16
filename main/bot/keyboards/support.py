from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn
from core.settings import settings


def kb_support_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("support", url=settings.SUPPORT_BOT_URL)))
    builder.row(back_btn("back_to_main", "menu:main"))
    return builder.as_markup()
