from __future__ import annotations

import logging

from aiogram import F, Bot, Router
from aiogram.types import Message

from bot.assets.texts import t
from clients.api import ApiNotFoundError, api_client

router = Router(name="support_answer")
logger = logging.getLogger(__name__)


def _is_forum_message(msg: Message) -> bool:
    return msg.chat.type in ("group", "supergroup") and msg.message_thread_id is not None


def _is_real_reply(msg: Message) -> bool:
    reply = msg.reply_to_message
    return reply is not None and reply.message_id != msg.message_thread_id


@router.message(lambda msg: _is_forum_message(msg) and _is_real_reply(msg) and not msg.from_user.is_bot)
async def forum_reply(msg: Message, bot: Bot) -> None:
    if msg.text and msg.text.startswith("."):
        return

    try:
        thread = await api_client.support.get_thread_by_topic(forum_chat_id=msg.chat.id, topic_id=msg.message_thread_id)
        mapping = await api_client.support.get_message_by_support(
            forum_chat_id=msg.chat.id,
            support_message_id=msg.reply_to_message.message_id,
        )
    except ApiNotFoundError:
        return

    try:
        if msg.text and msg.text.startswith("/reply"):
            reply_text = msg.text[len("/reply"):].strip()
            if not reply_text:
                return
            sent = await bot.send_message(
                chat_id=thread.user_id,
                text=reply_text,
                reply_to_message_id=mapping.user_message_id,
            )
        else:
            sent = await bot.copy_message(
                chat_id=thread.user_id,
                from_chat_id=msg.chat.id,
                message_id=msg.message_id,
            )

        await api_client.support.create_message_mapping(
            user_id=thread.user_id,
            forum_chat_id=thread.forum_chat_id,
            topic_id=thread.topic_id,
            support_message_id=msg.message_id,
            user_message_id=sent.message_id,
            original_support_message_id=mapping.support_message_id,
            original_user_message_id=mapping.user_message_id,
        )
        await msg.reply(t("event_reply_sent"))
    except Exception:
        logger.exception("Failed to send forum reply to client")
        await msg.reply(t("error_send_reply"))


@router.edited_message(lambda msg: _is_forum_message(msg) and not msg.from_user.is_bot)
async def forum_edit(msg: Message, bot: Bot) -> None:
    try:
        thread = await api_client.support.get_thread_by_topic(forum_chat_id=msg.chat.id, topic_id=msg.message_thread_id)
        mapping = await api_client.support.get_message_by_support(
            forum_chat_id=msg.chat.id,
            support_message_id=msg.message_id,
        )
    except ApiNotFoundError:
        return

    try:
        if msg.text:
            await bot.edit_message_text(
                text=msg.text,
                chat_id=thread.user_id,
                message_id=mapping.user_message_id,
                entities=msg.entities,
            )
        elif msg.caption is not None:
            await bot.edit_message_caption(
                chat_id=thread.user_id,
                message_id=mapping.user_message_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities,
            )
    except Exception:
        logger.exception("Failed to edit support reply in client chat")
