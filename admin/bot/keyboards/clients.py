from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn, t
from bot.keyboards.common import back_btn, nav_buttons


def kb_clients_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Поиск клиента", callback_data="admin:clients:search"))
    builder.row(InlineKeyboardButton(text="👥 Список клиентов", callback_data="admin:clients:recent:1"))
    builder.row(back_btn("admin:panel"))
    return builder.as_markup()


def kb_clients_list(*, items: list, page: int, total: int, per_page: int, query: str | None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        label = item.first_name or item.username or str(item.user_id)
        builder.row(
            InlineKeyboardButton(
                text=f"#{item.user_id} | {label}",
                callback_data=f"admin:user:{item.user_id}",
            )
        )
    total_pages = max(1, (total + per_page - 1) // per_page)
    nav = nav_buttons(page, total_pages, f"admin:clients:page:{query}" if query else "admin:clients:recent")
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🔎 Новый поиск", callback_data="admin:clients:search"))
    builder.row(back_btn("admin:clients:menu"))
    return builder.as_markup()


def kb_client_card(*, user_id: int, is_banned: bool, client_id: int | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            **btn(
                "cf_client_btn_ban_toggle",
                callback_data=f"admin:user:ban:{user_id}",
                text=t("cf_client_ban_status_locked" if is_banned else "cf_client_ban_status_unlocked"),
            )
        ),
        InlineKeyboardButton(**btn("send_message", callback_data=f"admin:user:msg:{user_id}")),
    )
    cid = client_id if client_id is not None else user_id
    builder.row(
        InlineKeyboardButton(
            text="📜 История активности",
            switch_inline_query_current_chat=f"log_history?client_id={cid}&search=",
        )
    )
    builder.row(InlineKeyboardButton(**btn("change_agreement", callback_data=f"admin:user:agreements:{user_id}")))
    builder.row(InlineKeyboardButton(**btn("refresh", callback_data=f"admin:user:refresh:{user_id}")))
    builder.row(back_btn("admin:clients:back"))
    return builder.as_markup()


def approve_send_message_ikb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data="admin:user:msg:approve")))
    builder.row(back_btn(f"admin:user:{user_id}"))
    return builder.as_markup()


def kb_agreements(*, user_id: int, agreements: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for agreement in agreements:
        title = getattr(agreement, "title", agreement.get("title") if isinstance(agreement, dict) else "—")
        aid = getattr(agreement, "agreement_id", getattr(agreement, "id", ""))
        builder.row(
            InlineKeyboardButton(
                text=f"📄 {title}",
                callback_data=f"admin:user:set-agreement:{user_id}:{aid}",
            )
        )
    builder.row(back_btn(f"admin:user:{user_id}"))
    return builder.as_markup()


def kb_log_detail(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back_to_client"),
            callback_data=f"admin:user:{user_id}",
        )
    )
    return builder.as_markup()

