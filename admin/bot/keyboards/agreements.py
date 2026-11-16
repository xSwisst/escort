from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn


def kb_agreements_admin_list(agreements: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in agreements:
        title = getattr(item, "title", item.get("title") if isinstance(item, dict) else "—")
        aid = getattr(item, "agreement_id", getattr(item, "id", ""))
        builder.row(InlineKeyboardButton(text=f"📄 {title}", callback_data=f"admin:agr:info:{aid}"))

    builder.row(InlineKeyboardButton(**btn("add", callback_data="admin:agr:new")))
    builder.row(back_btn("admin:panel"))
    return builder.as_markup()


def kb_agreement_admin_card(agreement_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("delete", callback_data=f"admin:agr:del:{agreement_id}")))
    builder.row(back_btn("admin:agreements:list"))
    return builder.as_markup()


def kb_confirm_delete_agreement(agreement_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data=f"admin:agr:del:confirm:{agreement_id}")))
    builder.row(back_btn(f"admin:agr:info:{agreement_id}"))
    return builder.as_markup()


def kb_approve_new_agreement() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data="admin:agr:new:approve")))
    builder.row(back_btn("admin:agreements:list"))
    return builder.as_markup()

