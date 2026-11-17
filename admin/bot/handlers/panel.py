from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import kb_panel
from bot.services import build_panel_text

router = Router(name="admin_panel")


async def _set_panel_anchor(state: FSMContext, *, chat_id: int, message_id: int) -> None:
    await state.update_data(admin_panel_chat_id=chat_id, admin_panel_message_id=message_id)


async def _load_panel_stats() -> tuple[int, int, int, int, int, int]:
    total_clients = 0
    total_forms = 0
    forms_city_1 = 0
    forms_city_2 = 0
    total_promos = 0
    total_agreements = 0

    try:
        clients_resp = await api_client.admin.list_clients(page=1, per_page=1)
        total_clients = clients_resp.total
    except Exception:
        pass

    try:
        forms_resp = await api_client.admin.list_forms()
        total_forms = len(forms_resp.items)
        forms_city_1 = sum(1 for f in forms_resp.items if getattr(f, "city_slot", 1) == 1)
        forms_city_2 = sum(1 for f in forms_resp.items if getattr(f, "city_slot", 1) == 2)
    except Exception:
        pass

    try:
        promos_resp = await api_client.admin.list_promos()
        total_promos = len(promos_resp.items)
    except Exception:
        pass

    try:
        agr_resp = await api_client.admin.list_agreements()
        total_agreements = len(agr_resp.items)
    except Exception:
        pass

    return total_clients, total_forms, total_promos, total_agreements, forms_city_1, forms_city_2


async def send_panel(message: Message, state: FSMContext) -> None:
    c, f, p, a, fc1, fc2 = await _load_panel_stats()
    text = build_panel_text(c, f, p, a, forms_city_1=fc1, forms_city_2=fc2)
    sent = await message.answer(text, parse_mode="HTML", reply_markup=kb_panel(client_count=c))
    await _set_panel_anchor(state, chat_id=sent.chat.id, message_id=sent.message_id)


async def edit_panel(call: CallbackQuery, state: FSMContext) -> None:
    c, f, p, a, fc1, fc2 = await _load_panel_stats()
    text = build_panel_text(c, f, p, a, forms_city_1=fc1, forms_city_2=fc2)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb_panel(client_count=c))
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=kb_panel(client_count=c))
    await _set_panel_anchor(state, chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.answer()


@router.callback_query(F.data == "admin:panel")
async def open_panel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await edit_panel(call, state)
