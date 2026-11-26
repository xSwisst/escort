from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn
from clients.api.schemas import CLIENT_LOG_SETTING_KEYS


def kb_settings_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("admin_settings_client_logs", callback_data="admin:settings:client_logs")))
    builder.row(back_btn("admin:panel", text_key="back_to_menu"))
    return builder.as_markup()


def kb_client_logs_settings(states: dict[str, bool]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key in CLIENT_LOG_SETTING_KEYS:
        enabled = bool(states.get(key, True))
        label = btn(f"client_log_label_{key}")["text"]
        tpl_key = "client_log_toggle_on" if enabled else "client_log_toggle_off"
        builder.row(
            InlineKeyboardButton(
                **btn(
                    tpl_key,
                    label=label,
                    callback_data=f"admin:settings:client_log_toggle:{key}",
                )
            )
        )
    builder.row(back_btn("admin:settings:menu", text_key="back_to_settings"))
    return builder.as_markup()
