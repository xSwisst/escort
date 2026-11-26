from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.types import Message

from bot.assets.texts import t
from bot.keyboards import kb_user_info
from clients.api import ApiNotFoundError, api_client
from bot.services import build_client_info_text, emit_support_info
from core.settings import settings

router = Router(name="support_question")
logger = logging.getLogger(__name__)


def _topic_name(msg: Message) -> str:
    full_name = " ".join(part for part in [msg.from_user.first_name, msg.from_user.last_name] if part).strip()
    return t("support_topic_name", full_name=full_name or str(msg.from_user.id))


async def _ensure_thread(msg: Message, bot: Bot):
    await api_client.support.bootstrap_client(
        user_id=msg.from_user.id,
        first_name=msg.from_user.first_name,
        last_name=msg.from_user.last_name,
        username=msg.from_user.username,
    )
    summary = await api_client.support.get_client_summary(msg.from_user.id)
    try:
        thread = await api_client.support.get_thread_by_user(msg.from_user.id)
        return thread, False, summary
    except ApiNotFoundError:
        pass

    topic = await bot.create_forum_topic(chat_id=settings.SUPPORT_FORUM_CHAT_ID, name=_topic_name(msg))
    thread = await api_client.support.upsert_thread(
        user_id=msg.from_user.id,
        forum_chat_id=settings.SUPPORT_FORUM_CHAT_ID,
        topic_id=int(topic.message_thread_id),
    )
    info_message = await bot.send_message(
        chat_id=thread.forum_chat_id,
        message_thread_id=thread.topic_id,
        text=build_client_info_text(summary),
        parse_mode="HTML",
        reply_markup=kb_user_info(msg.from_user.id),
    )
    try:
        await bot.pin_chat_message(chat_id=thread.forum_chat_id, message_id=info_message.message_id)
    except Exception:
        pass
    thread = await api_client.support.upsert_thread(
        user_id=msg.from_user.id,
        forum_chat_id=thread.forum_chat_id,
        topic_id=thread.topic_id,
        info_message_id=info_message.message_id,
    )
    return thread, True, summary


@router.message(F.chat.type == "private", ~F.via_bot)
async def client_message(msg: Message, bot: Bot) -> None:
    if msg.from_user is None or msg.from_user.is_bot:
        return
    if msg.text and msg.text.startswith("/"):
        return

    try:
        thread, created, summary = await _ensure_thread(msg, bot)
        if thread.is_banned:
            await msg.answer(t("error_banned"))
            return

        copied = await bot.copy_message(
            chat_id=thread.forum_chat_id,
            from_chat_id=msg.chat.id,
            message_id=msg.message_id,
            message_thread_id=thread.topic_id,
        )
        await api_client.support.create_message_mapping(
            user_id=msg.from_user.id,
            forum_chat_id=thread.forum_chat_id,
            topic_id=thread.topic_id,
            support_message_id=int(copied.message_id),
            user_message_id=int(msg.message_id),
        )

        # Check if this is the first real message to support (not /start)
        message_count = await api_client.support.count_user_messages(msg.from_user.id)
        if created or message_count == 1:
            await emit_support_info(
                event_type="message_to_support",
                payload={
                    "id": getattr(summary, "id", None),
                    "user_id": msg.from_user.id,
                    "first_name": msg.from_user.first_name or "",
                    "last_name": msg.from_user.last_name or "",
                    "username": msg.from_user.username,
                    "topic_id": thread.topic_id,
                },
                actor_id=msg.from_user.id,
                chat_id=msg.chat.id,
                message_id=msg.message_id,
            )
    except Exception:
        logger.exception("Failed to forward client message to support forum")
        await msg.answer(t("error_delivery_failed"))


@router.edited_message(F.chat.type == "private")
async def client_edit(msg: Message, bot: Bot) -> None:
    if msg.from_user is None or msg.from_user.is_bot:
        return
    try:
        mapping = await api_client.support.get_message_by_user(user_id=msg.from_user.id, user_message_id=msg.message_id)
    except ApiNotFoundError:
        return

    try:
        if msg.text:
            await bot.edit_message_text(
                text=msg.text,
                chat_id=mapping.forum_chat_id,
                message_id=mapping.support_message_id,
                entities=msg.entities,
            )
        elif msg.caption is not None:
            await bot.edit_message_caption(
                chat_id=mapping.forum_chat_id,
                message_id=mapping.support_message_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities,
            )
    except Exception:
        logger.exception("Failed to update forwarded support message")
