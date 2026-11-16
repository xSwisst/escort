from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.assets.texts import t
from bot.keyboards import kb_agreements, kb_user_info
from clients.api import ApiNotFoundError, api_client
from services import build_client_info_text

router = Router(name="support_info")


async def _load_thread_client(msg: Message):
    if not (msg.chat.type in ("group", "supergroup") and msg.message_thread_id):
        await msg.reply(t("error_forum_only"))
        return None
    try:
        return await api_client.support.get_thread_by_topic(forum_chat_id=msg.chat.id, topic_id=msg.message_thread_id)
    except ApiNotFoundError:
        await msg.reply(t("error_thread_not_found"))
        return None


@router.message(Command("info"), lambda msg: msg.chat.type in ("group", "supergroup") and msg.message_thread_id is not None)
async def cmd_info(msg: Message) -> None:
    thread = await _load_thread_client(msg)
    if thread is None:
        return
    try:
        summary = await api_client.support.get_client_summary(thread.user_id)
    except ApiNotFoundError:
        await msg.reply(t("error_client_not_found"))
        return
    await msg.answer(build_client_info_text(summary), parse_mode="HTML", reply_markup=kb_user_info(thread.user_id))


@router.callback_query(F.data.startswith("support:change-agreement:"))
async def change_agreement(call: CallbackQuery) -> None:
    user_id = int(call.data.split(":")[2])
    agreements = await api_client.support.list_agreements()
    await call.message.edit_text(
        t("support_client_agreement_choose"),
        parse_mode="HTML",
        reply_markup=kb_agreements(agreements.items, user_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("support:set-agreement:"))
async def set_agreement(call: CallbackQuery) -> None:
    _, _, user_id_raw, agreement_id = call.data.split(":", 3)
    user_id = int(user_id_raw)
    try:
        await api_client.support.set_client_agreement(user_id, agreement_id)
        summary = await api_client.support.get_client_summary(user_id)
    except ApiNotFoundError:
        await call.answer(t("error_agreement_not_found"), show_alert=True)
        return
    await call.message.edit_text(
        build_client_info_text(summary),
        parse_mode="HTML",
        reply_markup=kb_user_info(user_id),
    )
    await call.answer(t("support_client_agreement_changed"))


@router.callback_query(F.data.startswith("support:back-user:"))
@router.callback_query(F.data.startswith("support:refresh-user:"))
async def refresh_client_card(call: CallbackQuery) -> None:
    user_id = int(call.data.split(":")[2])
    try:
        summary = await api_client.support.get_client_summary(user_id)
    except ApiNotFoundError:
        await call.answer(t("error_client_not_found"), show_alert=True)
        return
    await call.message.edit_text(
        build_client_info_text(summary),
        parse_mode="HTML",
        reply_markup=kb_user_info(user_id),
    )
    await call.answer()
