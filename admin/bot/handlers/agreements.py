from __future__ import annotations

import secrets
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.texts import t
from bot.keyboards import (
    kb_agreement_admin_card,
    kb_agreements_admin_list,
    kb_approve_new_agreement,
    kb_back,
    kb_confirm_delete_agreement,
)
from bot.states import VANewAgreement
from clients.api import api_client

router = Router(name="admin_agreements")


@router.callback_query(F.data == "admin:agreements:list")
async def show_agreements_list(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    resp = await api_client.admin.list_agreements()
    agreements = resp.items
    text = t("va_admin_agreements_caption")
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb_agreements_admin_list(agreements))
    await call.answer()


@router.callback_query(F.data.startswith("admin:agr:info:"))
async def show_agreement_card(call: CallbackQuery) -> None:
    agreement_id = call.data.split(":")[3]
    resp = await api_client.admin.list_agreements()
    agreement = next(
        (a for a in resp.items if getattr(a, "agreement_id", getattr(a, "id", None)) == agreement_id),
        None,
    )
    if not agreement:
        await call.answer(t("va_admin_agreement_not_found"), show_alert=True)
        return

    text = t(
        "va_admin_agreement_info",
        agreement_id=agreement.agreement_id,
        agreement_name=getattr(agreement, "title", "—"),
        agreement_url=getattr(agreement, "document_url", "—") or "—",
        creater_id="—",
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb_agreement_admin_card(agreement_id))
    await call.answer()


@router.callback_query(F.data.startswith("admin:agr:del:confirm:"))
async def confirm_delete_agreement(call: CallbackQuery, state: FSMContext) -> None:
    agreement_id = call.data.split(":")[4]
    try:
        await api_client.admin.delete_agreement(agreement_id)
        await call.answer(t("va_admin_agreement_deleted_answer"))
    except Exception as exc:
        await call.answer(f"Ошибка удаления: {exc}", show_alert=True)
        return
    await show_agreements_list(call, state)


@router.callback_query(F.data.startswith("admin:agr:del:"))
async def ask_delete_agreement(call: CallbackQuery) -> None:
    agreement_id = call.data.split(":")[3]
    await call.message.edit_text(
        t("va_admin_agreement_delete_confirm"),
        parse_mode="HTML",
        reply_markup=kb_confirm_delete_agreement(agreement_id),
    )
    await call.answer()


@router.callback_query(F.data == "admin:agr:new")
async def ask_new_agreement(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VANewAgreement.name)
    await state.update_data(va_message_id=call.message.message_id)
    await call.message.edit_text(
        t("va_admin_new_agreement_step1"),
        parse_mode="HTML",
        reply_markup=kb_back("admin:agreements:list"),
    )
    await call.answer()


@router.message(StateFilter(VANewAgreement.name), F.chat.type == "private")
async def process_new_agreement_name(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    data = await state.get_data()
    try:
        await message.delete()
    except Exception:
        pass
    if not title:
        return
    await state.update_data(new_agreement_title=title)
    await state.set_state(VANewAgreement.url)
    msg_id = data.get("va_message_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=t("va_admin_new_agreement_step2"),
                parse_mode="HTML",
                reply_markup=kb_back("admin:agreements:list"),
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        t("va_admin_new_agreement_step2"),
        parse_mode="HTML",
        reply_markup=kb_back("admin:agreements:list"),
    )
    await state.update_data(va_message_id=sent.message_id)


@router.message(StateFilter(VANewAgreement.url), F.chat.type == "private")
async def process_new_agreement_url(message: Message, state: FSMContext) -> None:
    url = (message.text or "").strip()
    data = await state.get_data()
    try:
        await message.delete()
    except Exception:
        pass
    await state.update_data(new_agreement_url=url)
    msg_id = data.get("va_message_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=t("va_admin_agreement_confirm_add"),
                parse_mode="HTML",
                reply_markup=kb_approve_new_agreement(),
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        t("va_admin_agreement_confirm_add"),
        parse_mode="HTML",
        reply_markup=kb_approve_new_agreement(),
    )
    await state.update_data(va_message_id=sent.message_id)


@router.callback_query(F.data == "admin:agr:new:approve")
async def approve_add_agreement(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    title = str(data.get("new_agreement_title", "")).strip()
    url = str(data.get("new_agreement_url", "")).strip()
    if not title or not url:
        await call.answer(t("va_admin_agreement_missing"), show_alert=True)
        return
    agreement_id = secrets.token_hex(4)
    try:
        await api_client.admin.create_agreement(
            {"agreement_id": agreement_id, "title": title, "document_url": url or None}
        )
        await call.answer(t("va_admin_agreement_added_answer"))
    except Exception as exc:
        await call.answer(f"❌ Ошибка создания: {exc}", show_alert=True)
        return
    await state.clear()
    call.data = "admin:agreements:list"
    await show_agreements_list(call, state)

