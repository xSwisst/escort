from aiogram.types import InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from core.settings import settings


def kb_main_menu(*, show_web_app: bool = True):
    builder = InlineKeyboardBuilder()
    web_app_url = str(settings.WEB_APP_URL or "").strip()
    builder.row(InlineKeyboardButton(**btn("profile", callback_data="menu:profile")))
    builder.row(InlineKeyboardButton(**btn("models", callback_data="menu:models")))
    builder.row(InlineKeyboardButton(**btn("search_code", callback_data="menu:search_code")))
    builder.row(InlineKeyboardButton(**btn("information", callback_data="menu:info")))
    builder.row(InlineKeyboardButton(**btn("support", callback_data="menu:support")))
    if web_app_url and show_web_app:
        builder.row(InlineKeyboardButton(**btn("open_web_app"), web_app=WebAppInfo(url=web_app_url)))
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()
