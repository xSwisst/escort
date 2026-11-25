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


def kb_client_card(
    *,
    user_id: int,
    is_banned: bool,
    is_pinned: bool = False,
    client_id: int | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Ряд 0: Закрепить / Открепить
    pin_btn_key = "unpin_client" if is_pinned else "pin_client"
    builder.row(
        InlineKeyboardButton(**btn(pin_btn_key, callback_data=f"admin:user:pin:{user_id}"))
    )

    # Ряд 1: История действий
    cid = client_id if client_id is not None else user_id
    builder.row(
        InlineKeyboardButton(
            **btn("client_actions", switch_inline_query_current_chat=f"log_history?client_id={cid}&search=")
        )
    )

    # Ряд 2: Заказы | Операции
    builder.row(
        InlineKeyboardButton(
            **btn("client_orders", switch_inline_query_current_chat=f"get_client_orders?client_id={user_id}&search=")
        ),
        InlineKeyboardButton(
            **btn("client_transactions", switch_inline_query_current_chat=f"get_client_transaction?client_id={user_id}&search=")
        ),
    )

    # Ряд 3: Заявки на пополнение
    builder.row(
        InlineKeyboardButton(
            **btn("client_payments", switch_inline_query_current_chat=f"get_client_payments?client_id={user_id}&search=")
        )
    )

    # Ряд 4: Отправить сообщение
    builder.row(InlineKeyboardButton(**btn("send_message", callback_data=f"admin:user:msg:{user_id}")))

    # Ряд 5: Управление балансом
    builder.row(InlineKeyboardButton(**btn("manage_balance", callback_data=f"admin:user:balance:{user_id}")))

    # Ряд 6: Соглашение | Заблокирован/Разблокирован
    ban_text = t("client_ban_status_locked" if is_banned else "client_ban_status_unlocked")
    builder.row(
        InlineKeyboardButton(**btn("change_agreement", callback_data=f"admin:user:agreements:{user_id}")),
        InlineKeyboardButton(
            **btn("client_ban_toggle", callback_data=f"admin:user:ban:{user_id}", text=ban_text)
        ),
    )

    # Ряд 7: Обновить
    builder.row(InlineKeyboardButton(**btn("refresh", callback_data=f"admin:user:refresh:{user_id}")))

    # Ряд 8: Назад в меню
    builder.row(back_btn("admin:panel", text_key="back_to_menu"))
    return builder.as_markup()


def manage_balance_ikb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("balance_set", callback_data=f"admin:user:bal:set:{user_id}")))
    builder.row(InlineKeyboardButton(**btn("balance_add", callback_data=f"admin:user:bal:add:{user_id}")))
    builder.row(InlineKeyboardButton(**btn("balance_sub", callback_data=f"admin:user:bal:sub:{user_id}")))
    builder.row(back_btn(f"admin:user:{user_id}", text_key="back_to_client"))
    return builder.as_markup()


def confirm_balance_ikb(user_id: int, notify: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    notify_btn = "balance_notify_off" if notify else "balance_notify_on"
    builder.row(InlineKeyboardButton(**btn(notify_btn, callback_data=f"admin:user:bal:toggle-notify:{user_id}")))
    builder.row(
        back_btn(f"admin:user:balance:{user_id}", text_key="back_to_balance"),
        InlineKeyboardButton(**btn("confirm", callback_data=f"admin:user:bal:confirm:{user_id}")),
    )
    return builder.as_markup()


def balance_input_cancel_ikb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(back_btn(f"admin:user:balance:{user_id}", text_key="back_to_balance"))
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

