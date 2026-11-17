import logging
from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.assets.texts import t
from bot.keyboards import kb_client_card, kb_log_detail, kb_model_card
from clients.api import api_client
from bot.services import (
    build_client_card_text,
    build_log_detail_text,
    build_model_card_text,
    is_admin_allowed,
)

from .panel import send_panel

logger = logging.getLogger(__name__)

router = Router(name="admin_start")


@router.message(CommandStart(), F.chat.type == "private")
@router.message(Command("panel"), F.chat.type == "private")
async def cmd_start(message: Message, state: FSMContext, command: CommandObject | None = None) -> None:
    if not is_admin_allowed(message.from_user.id):
        await message.answer(t("access_denied"))
        return

    # Обработка диплинка для открытия карточки анкеты: /start open_model_{code} или open_form_{code}
    if command and command.args and (command.args.startswith("open_model_") or command.args.startswith("open_form_")):
        raw_code = command.args.split("_", 2)[2].strip()
        if raw_code:
            await state.clear()
            form = None
            try:
                form = await api_client.admin.get_form(raw_code)
            except Exception as exc:
                logger.debug("Failed to get form %s: %s", raw_code, exc)

            if form:
                text = build_model_card_text(form)
                kb = kb_model_card(form, form.city_slot)
                await message.answer(text, parse_mode="HTML", reply_markup=kb)
                return
            else:
                await message.answer(t("va_answer_not_found"))
                return

    # Обработка диплинка для открытия лога: /start get_log_{id}
    if command and command.args and command.args.startswith("get_log_"):
        raw_id = command.args.replace("get_log_", "", 1).strip()
        if raw_id.isdigit():
            log_id = int(raw_id)
            await state.clear()
            try:
                log_data = await api_client.admin.get_client_log(log_id)
            except Exception:
                await message.answer(t("client_log_not_found", log_id=log_id))
                return

            client = None
            try:
                client = await api_client.admin.get_client(log_data.user_id)
            except Exception:
                pass

            text = build_log_detail_text(log_data, client)
            markup = kb_log_detail(user_id=log_data.user_id)
            sent = await message.answer(text, parse_mode="HTML", reply_markup=markup)
            await state.update_data(admin_panel_chat_id=sent.chat.id, admin_panel_message_id=sent.message_id)
            return

    # Обработка диплинка для открытия карточки клиента: /start open_client_{id}
    if command and command.args and command.args.startswith("open_client_"):
        raw_id = command.args.replace("open_client_", "", 1).strip()
        if raw_id.isdigit():
            client_id = int(raw_id)
            await state.clear()
            client = None
            try:
                client = await api_client.admin.get_client_by_db_id(client_id)
            except Exception as exc:
                logger.debug("Failed to get client by db_id %s: %s", client_id, exc)

            if not client:
                try:
                    client = await api_client.admin.get_client(client_id)
                except Exception as exc:
                    logger.debug("Failed to get client by user_id %s: %s", client_id, exc)

            if client:
                await message.answer(
                    build_client_card_text(client),
                    parse_mode="HTML",
                    reply_markup=kb_client_card(
                        user_id=client.user_id,
                        is_banned=client.is_banned,
                        client_id=getattr(client, "id", None),
                    ),
                )
                return
            else:
                await message.answer(t("cf_client_not_found", client_id=client_id))
                return

    await state.clear()
    await send_panel(message, state)
