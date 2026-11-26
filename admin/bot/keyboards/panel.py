from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn, t


def kb_panel(*, client_count: int = 0, is_owner: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            **btn(
                "client_list",
                text=t("va_client_list_button", client_count=max(0, int(client_count or 0))),
                switch_inline_query_current_chat="my_clients?search=",
            )
        )
    )
    builder.row(
        InlineKeyboardButton(**btn("forms_worker", callback_data="admin:forms:city")),
        InlineKeyboardButton(**btn("manage_promo", callback_data="admin:promos:list:1")),
    )
    builder.row(
        InlineKeyboardButton(**btn("malling", callback_data="admin:malling:menu")),
        InlineKeyboardButton(**btn("admin_settings", callback_data="admin:settings:menu")),
    )
    if is_owner:
        builder.row(
            InlineKeyboardButton(**btn("cards", callback_data="admin:cards:list:1")),
            InlineKeyboardButton(**btn("va_admin_agreements", callback_data="admin:agreements:list")),
        )
    return builder.as_markup()
