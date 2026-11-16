from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn
from core.settings import settings


def kb_info(*, document_url: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(**btn("guarantees", callback_data="info:guarantees")),
        InlineKeyboardButton(**btn("additionals", callback_data="info:additionals")),
    )
    builder.row(InlineKeyboardButton(**btn("faq", callback_data="info:faq")))
    builder.row(InlineKeyboardButton(**btn("support", url=settings.SUPPORT_BOT_URL)))
    if document_url:
        builder.row(InlineKeyboardButton(**btn("agreement", url=document_url)))
    builder.row(back_btn("back_to_main", "menu:main"))
    return builder.as_markup()


def kb_faq(selected: int = 1) -> InlineKeyboardMarkup:
    labels = []
    for number in range(1, 4):
        text = f"\u2022 {number} \u2022" if number == selected else str(number)
        labels.append(InlineKeyboardButton(text=text, callback_data=f"question:{number}"))
    return InlineKeyboardMarkup(inline_keyboard=[labels, [back_btn("back_to_info", "menu:info")]])


def kb_back_info() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn("back_to_info", "menu:info")]])


def kb_back_additionals() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn("back_to_additionals", "info:additionals")]])


def kb_additionals_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("additionals_info", callback_data="info:add_info")))
    builder.row(
        InlineKeyboardButton(**btn("shootings", callback_data="info:sub:shootings")),
        InlineKeyboardButton(**btn("accompaniment", callback_data="info:sub:accompaniment")),
    )
    builder.row(
        InlineKeyboardButton(**btn("relations", callback_data="info:sub:relations")),
        InlineKeyboardButton(**btn("promo_section", callback_data="info:sub:promo_s")),
    )
    builder.row(InlineKeyboardButton(**btn("hostess", callback_data="info:sub:hostess")))
    builder.row(back_btn("back_to_info", "menu:info"))
    return builder.as_markup()

