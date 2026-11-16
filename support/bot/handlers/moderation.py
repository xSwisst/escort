from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.assets.texts import t
from clients.api import ApiNotFoundError, api_client
from services import emit_support_info

router = Router(name="support_moderation")


async def _set_ban(msg: Message, *, is_banned: bool) -> None:
    if not (msg.chat.type in ("group", "supergroup") and msg.message_thread_id):
        await msg.reply(t("error_forum_only"))
        return
    try:
        thread = await api_client.support.get_thread_by_topic(forum_chat_id=msg.chat.id, topic_id=msg.message_thread_id)
        await api_client.support.set_ban(user_id=thread.user_id, is_banned=is_banned)
    except ApiNotFoundError:
        await msg.reply(t("error_thread_not_found"))
        return
    await msg.reply(t("event_ban_enabled" if is_banned else "event_ban_disabled"))
    await emit_support_info(
        event_type="support_ban_enabled" if is_banned else "support_ban_disabled",
        payload={"user_id": thread.user_id},
        actor_id=thread.user_id,
        chat_id=msg.chat.id,
        message_id=msg.message_id,
    )


@router.message(Command("ban"))
async def cmd_ban(msg: Message, bot: Bot) -> None:
    del bot
    await _set_ban(msg, is_banned=True)


@router.message(Command("unban"))
async def cmd_unban(msg: Message, bot: Bot) -> None:
    del bot
    await _set_ban(msg, is_banned=False)
