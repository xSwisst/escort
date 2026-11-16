from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.assets.texts import btn
from bot.keyboards.common import back_btn, nav_buttons


def format_card_number_masked(num: str) -> str:
    cleaned = "".join(c for c in num if c.isdigit())
    if len(cleaned) >= 12:
        return f"{cleaned[:4]} •••• •••• {cleaned[-4:]}"
    elif len(cleaned) >= 4:
        return f"•••• {cleaned[-4:]}"
    return num


def kb_cards_list(cards: list, page: int = 1, per_page: int = 8) -> InlineKeyboardMarkup:
    rows = []
    total = len(cards)
    total_pages = max(1, -(-total // per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    chunk = cards[start : start + per_page]

    for item in chunk:
        card_id = getattr(item, "id", item.get("id") if isinstance(item, dict) else 0)
        card_number = getattr(item, "card_number", item.get("card_number") if isinstance(item, dict) else "")
        min_amount = getattr(item, "min_amount", item.get("min_amount") if isinstance(item, dict) else 0)
        max_amount = getattr(item, "max_amount", item.get("max_amount") if isinstance(item, dict) else 0)
        is_active = getattr(item, "is_active", item.get("is_active") if isinstance(item, dict) else True)

        status_icon = "🟢" if is_active else "🔴"
        masked = format_card_number_masked(card_number)
        min_str = f"{min_amount:,}".replace(",", " ")
        max_str = f"{max_amount:,}".replace(",", " ")
        btn_text = f"💳 {masked} ({min_str} — {max_str} ₽) {status_icon}"

        rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"admin:card:info:{card_id}")])

    nav = nav_buttons(page, total_pages, "admin:cards:list")
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(**btn("add", callback_data="admin:card:new"))])
    rows.append([back_btn("admin:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_card_card(card) -> InlineKeyboardMarkup:
    card_id = getattr(card, "id", card.get("id") if isinstance(card, dict) else 0)
    is_active = getattr(card, "is_active", card.get("is_active") if isinstance(card, dict) else True)

    toggle_btn = (
        InlineKeyboardButton(text="🔴 Отключить", callback_data=f"admin:card:toggle:{card_id}")
        if is_active
        else InlineKeyboardButton(text="🟢 Включить", callback_data=f"admin:card:toggle:{card_id}")
    )

    rows = [
        [toggle_btn],
        [InlineKeyboardButton(**btn("delete", callback_data=f"admin:card:del:{card_id}"))],
        [back_btn("admin:cards:list:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_confirm_delete_card(card_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data=f"admin:card:del:confirm:{card_id}"))],
        [back_btn(f"admin:card:info:{card_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_approve_new_card() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data="admin:card:new:approve"))],
        [back_btn("admin:cards:list:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
