from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.assets.texts import t
from bot.keyboards.settings import kb_client_logs_settings, kb_settings_menu
from clients.api import api_client

router = Router(name="admin_settings")


@router.callback_query(F.data == "admin:settings:menu")
async def show_settings_menu(call: CallbackQuery) -> None:
    await call.message.edit_text(
        t("admin_settings_caption"),
        parse_mode="HTML",
        reply_markup=kb_settings_menu(),
    )
    await call.answer()


@router.callback_query(F.data == "admin:settings:client_logs")
async def show_client_logs_settings(call: CallbackQuery) -> None:
    states = await api_client.admin.get_client_log_settings(call.from_user.id)
    await call.message.edit_text(
        t("admin_settings_client_logs_caption"),
        parse_mode="HTML",
        reply_markup=kb_client_logs_settings(states),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:settings:client_log_toggle:"))
async def toggle_client_log_setting(call: CallbackQuery) -> None:
    setting_key = call.data.rsplit(":", 1)[1]
    try:
        states = await api_client.admin.toggle_client_log_setting(call.from_user.id, setting_key)
    except ValueError:
        await call.answer()
        return
    await call.message.edit_reply_markup(reply_markup=kb_client_logs_settings(states))
    await call.answer()
