from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.texts import t
from bot.keyboards import (
    kb_approve_new_promo,
    kb_back,
    kb_confirm_delete_promo,
    kb_promo_card,
    kb_promos_list,
)
from bot.states import VANewPromo
from clients.api import api_client
from shared.utils.date import format_datetime_ru

router = Router(name="admin_promos")


async def _resolve_admin_id(tg_user) -> int:
    admin = await api_client.admin.get_or_create_admin(
        tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )
    return admin.id


@router.callback_query(F.data.startswith("admin:promos:list:"))
async def show_promos_list(call: CallbackQuery, state: FSMContext, page: int | None = None) -> None:
    await state.clear()
    if page is None:
        page = int(call.data.split(":")[3])
    admin_id = await _resolve_admin_id(call.from_user)
    resp = await api_client.admin.list_promos(admin_id=admin_id)
    promos = resp.items
    await call.message.edit_text(t("va_promo_list"), parse_mode="HTML", reply_markup=kb_promos_list(promos, page=page))
    await call.answer()


@router.callback_query(F.data.startswith("admin:promo:info:"))
async def show_promo_card(call: CallbackQuery) -> None:
    name = call.data.split(":")[3]
    admin_id = await _resolve_admin_id(call.from_user)
    resp = await api_client.admin.list_promos(admin_id=admin_id)
    promo = next((p for p in resp.items if p.name == name), None)
    if not promo:
        await call.answer(t("va_promo_answer_not_found"), show_alert=True)
        return

    text = t(
        "va_promo_info",
        name=promo.name,
        amount=promo.discount,
        discount=promo.discount,
        created_at=format_datetime_ru(promo.created_at),
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb_promo_card(name))
    await call.answer()


@router.callback_query(F.data.startswith("admin:promo:del:confirm:"))
async def confirm_delete_promo(call: CallbackQuery, state: FSMContext) -> None:
    name = call.data.split(":")[4]
    try:
        admin_id = await _resolve_admin_id(call.from_user)
        await api_client.admin.delete_promo(name, admin_id=admin_id)
        await call.answer(t("va_promo_deleted_answer"))
    except Exception as exc:
        await call.answer(f"Ошибка удаления: {exc}", show_alert=True)
        return
    await show_promos_list(call, state, page=1)


@router.callback_query(F.data.startswith("admin:promo:del:"))
async def ask_delete_promo(call: CallbackQuery) -> None:
    name = call.data.split(":")[3]
    await call.message.edit_text(
        t("va_promo_delete_confirm"),
        parse_mode="HTML",
        reply_markup=kb_confirm_delete_promo(name),
    )
    await call.answer()


@router.callback_query(F.data == "admin:promo:new")
async def ask_new_promo(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VANewPromo.sum)
    await state.update_data(
        promo_bot_msg_id=call.message.message_id,
        promo_bot_chat_id=call.message.chat.id,
    )
    await call.message.edit_text(t("va_promo_new_step1"), parse_mode="HTML", reply_markup=kb_back("admin:promos:list:1"))
    await call.answer()


@router.message(StateFilter(VANewPromo.sum), F.chat.type == "private")
async def process_new_promo(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    bot_msg_id = data.get("promo_bot_msg_id")
    chat_id = data.get("promo_bot_chat_id") or message.chat.id

    parts = [p.strip() for p in raw.split(";") if p.strip()]
    if len(parts) not in (1, 2) or not parts[0].isdigit() or int(parts[0]) <= 0:
        if bot_msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=t("va_promo_sum_wrong"),
                    parse_mode="HTML",
                    reply_markup=kb_back("admin:promos:list:1"),
                )
                return
            except Exception:
                pass
        sent = await message.answer(t("va_promo_sum_wrong"), parse_mode="HTML", reply_markup=kb_back("admin:promos:list:1"))
        await state.update_data(promo_bot_msg_id=sent.message_id)
        return

    discount = int(parts[0])
    name = parts[1] if len(parts) == 2 else f"PROMO{discount}"

    await state.update_data(new_promo_discount=discount, new_promo_name=name)
    confirm_text = t("va_promo_confirm_add", name=name, amount=discount)
    if bot_msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=confirm_text,
                parse_mode="HTML",
                reply_markup=kb_approve_new_promo(),
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        confirm_text,
        parse_mode="HTML",
        reply_markup=kb_approve_new_promo(),
    )
    await state.update_data(promo_bot_msg_id=sent.message_id)


@router.callback_query(F.data == "admin:promo:new:approve")
async def approve_new_promo(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    discount = data.get("new_promo_discount")
    name = data.get("new_promo_name")
    await state.clear()
    if not discount:
        return

    try:
        admin_id = await _resolve_admin_id(call.from_user)
        await api_client.admin.create_promo({"name": name, "discount": discount}, admin_id=admin_id)
        await call.answer(t("va_promo_added_answer"))
    except Exception as exc:
        await call.answer(f"Ошибка создания: {exc}", show_alert=True)

    call.data = "admin:promos:list:1"
    await show_promos_list(call, state)
