from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn, nav_buttons


def kb_promos_list(promos: list, page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    rows = []
    total = len(promos)
    total_pages = max(1, -(-total // per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    chunk = promos[start : start + per_page]

    for item in chunk:
        name = getattr(item, "name", item.get("name") if isinstance(item, dict) else "—")
        amount = getattr(item, "discount", getattr(item, "sum", 0))
        rows.append([InlineKeyboardButton(text=f"💌 {name} ({amount} RUB)", callback_data=f"admin:promo:info:{name}")])

    nav = nav_buttons(page, total_pages, "admin:promos:list")
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(**btn("add", callback_data="admin:promo:new"))])
    rows.append([back_btn("admin:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_promo_card(name: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("delete", callback_data=f"admin:promo:del:{name}"))],
        [back_btn("admin:promos:list:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_confirm_delete_promo(name: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data=f"admin:promo:del:confirm:{name}"))],
        [back_btn(f"admin:promo:info:{name}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_approve_new_promo() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data="admin:promo:new:approve"))],
        [back_btn("admin:promos:list:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

