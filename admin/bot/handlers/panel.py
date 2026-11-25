from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from bot.keyboards import kb_panel
from bot.services import build_panel_text, is_owner
from clients.api import api_client

router = Router(name="admin_panel")


async def _set_panel_anchor(state: FSMContext, *, chat_id: int, message_id: int) -> None:
    await state.update_data(admin_panel_chat_id=chat_id, admin_panel_message_id=message_id)


async def _load_panel_data(tg_user: User) -> tuple[str, bool, int]:
    admin = await api_client.admin.get_or_create_admin(
        tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )

    stats = await api_client.admin.get_worker_client_stats(admin.id)
    total_clients = stats.all

    total_forms = 0
    forms_city_1 = 0
    forms_city_2 = 0
    total_promos = 0

    try:
        forms_resp = await api_client.admin.list_forms(admin_id=admin.id)
        total_forms = len(forms_resp.items)
        forms_city_1 = sum(1 for f in forms_resp.items if getattr(f, "city_slot", 1) == 1)
        forms_city_2 = sum(1 for f in forms_resp.items if getattr(f, "city_slot", 1) == 2)
    except Exception:
        pass

    try:
        promos_resp = await api_client.admin.list_promos(admin_id=admin.id)
        total_promos = len(promos_resp.items)
    except Exception:
        pass

    bot_info = await api_client.admin.get_main_bot_info()
    username = (bot_info.username or "").lstrip("@").strip()
    bot_name = bot_info.full_name or "ESCORT V1"
    bot_link_text = f"@{username}" if username else "Недоступно"
    service_status = "Работает" if bot_info.is_alive else "Недоступен"
    service_status_emoji = "🟢" if bot_info.is_alive else "🔴"
    referral_link = f"https://t.me/{username}?start=r_{admin.id}" if username else f"r_{admin.id}"

    text = build_panel_text(
        total_clients=total_clients,
        total_forms=total_forms,
        total_promos=total_promos,
        forms_city_1=forms_city_1,
        forms_city_2=forms_city_2,
        bot_name=bot_name,
        bot_link_text=bot_link_text,
        service_status=service_status,
        service_status_emoji=service_status_emoji,
        referral_link=referral_link,
        today=stats.today,
        month=stats.month,
    )
    return text, is_owner(tg_user.id), total_clients


async def send_panel(message: Message, state: FSMContext) -> None:
    text, owner_flag, total_clients = await _load_panel_data(message.from_user)
    sent = await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=kb_panel(client_count=total_clients, is_owner=owner_flag),
    )
    await _set_panel_anchor(state, chat_id=sent.chat.id, message_id=sent.message_id)


async def edit_panel(call: CallbackQuery, state: FSMContext) -> None:
    text, owner_flag, total_clients = await _load_panel_data(call.from_user)
    markup = kb_panel(client_count=total_clients, is_owner=owner_flag)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=markup)
    await _set_panel_anchor(state, chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.answer()


@router.callback_query(F.data == "admin:panel")
async def open_panel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await edit_panel(call, state)
