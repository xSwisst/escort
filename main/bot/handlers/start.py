import logging

from aiogram import Bot, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.media import get_banner_file
from bot.assets.texts import btn, t
from bot.handlers.models_shared import get_form_card_payload
from bot.keyboards.common import main_reply_kb
from bot.keyboards.menu import kb_main_menu
from bot.keyboards.start import kb_accept_agreement
from clients.api import api_client
from shared.bot.utils.media_banner import (
    answer_banner,
    answer_photo,
    bot_send_banner,
    bot_send_photo,
    edit_banner,
)
from utils.deeplink import parse_deeplink
from utils.helpers import models_banner_media

logger = logging.getLogger(__name__)
router = Router(name="start")
MAIN_MENU_REPLY_TEXT = btn("main_menu_reply")["text"]


async def _show_main_menu(event: Message | CallbackQuery, bot: Bot) -> None:
    reply_keyboard = main_reply_kb(is_admin=False)
    if isinstance(event, CallbackQuery):
        await edit_banner(
            event.message,
            t("main_menu_caption"),
            banner=get_banner_file("main-menu-banner"),
            reply_markup=kb_main_menu(show_web_app=True),
        )
    else:
        await event.answer(t("butterfly_emoji"), reply_markup=reply_keyboard)
        await answer_banner(
            event,
            t("main_menu_caption"),
            banner=get_banner_file("main-menu-banner"),
            reply_markup=kb_main_menu(show_web_app=True),
        )


@router.message(CommandStart())
async def cmd_start(
    msg: Message,
    command: CommandObject,
    state: FSMContext,
    bot: Bot,
):
    await state.clear()
    bootstrap = await api_client.clients.bootstrap(
        user_id=msg.from_user.id,
        first_name=msg.from_user.first_name,
        last_name=msg.from_user.last_name,
        username=msg.from_user.username,
    )
    payload = parse_deeplink((command.args or "").strip() if command else "")

    if bootstrap.client.has_accepted_agreement:
        if payload.action == "open_model" and payload.action_arg:
            card = await get_form_card_payload(
                msg.from_user.id,
                payload.action_arg,
                fallback_media=models_banner_media(),
            )
            if card:
                media_ref, text, markup = card
                await msg.answer(t("butterfly_emoji"), reply_markup=main_reply_kb(is_admin=False))
                await answer_photo(
                    msg,
                    text,
                    media_ref,
                    reply_markup=markup,
                )
                return
            logger.warning("open_model deep link: form not found code=%s", payload.action_arg)
        await _show_main_menu(msg, bot)
        return

    agreement = bootstrap.agreement
    if agreement is None:
        await api_client.clients.accept_agreement(msg.from_user.id)
        await _show_main_menu(msg, bot)
        return

    await answer_banner(
        msg,
        t("agreement_caption"),
        banner=get_banner_file("agreement-banner"),
        reply_markup=kb_accept_agreement(
            url=agreement.document_url or None,
            name=agreement.title,
            action=payload.action,
            action_arg=payload.action_arg,
        ),
    )


@router.callback_query(F.data.startswith("start:accept"))
async def accept_agreement(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    pending_action = parts[2] if len(parts) > 2 else None
    pending_arg = parts[3] if len(parts) > 3 else None

    await api_client.clients.accept_agreement(call.from_user.id)
    await call.answer()

    if pending_action == "open_model" and pending_arg:
        card = await get_form_card_payload(
            call.from_user.id,
            pending_arg,
            fallback_media=models_banner_media(),
        )
        if card:
            media_ref, text, markup = card
            try:
                await call.message.delete()
            except Exception:
                pass
            await bot.send_message(call.message.chat.id, t("butterfly_emoji"), reply_markup=main_reply_kb(is_admin=False))
            await bot_send_photo(
                bot,
                call.message.chat.id,
                text,
                media_ref,
                reply_markup=markup,
            )
            return
    await _show_main_menu(call, bot)


@router.callback_query(F.data.in_({"menu:main", "main:menu", "back-main", "action:back"}))
async def cb_main_menu(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await call.answer()
    await _show_main_menu(call, bot)


@router.message(F.text.in_({MAIN_MENU_REPLY_TEXT, "/menu"}) | F.text.startswith("🦋"))
async def reply_main_menu(msg: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await msg.answer(text=t("butterfly_emoji"), reply_markup=main_reply_kb(is_admin=False))
    await answer_banner(msg, t("main_menu_caption"), banner=get_banner_file("main-menu-banner"), reply_markup=kb_main_menu(show_web_app=True))
