from __future__ import annotations

import logging
from urllib.parse import parse_qs

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from bot.assets.texts import t
from bot.keyboards import kb_log_detail
from bot.services import build_log_detail_text
from shared.utils.date import format_datetime_ru

logger = logging.getLogger(__name__)

router = Router(name="client_logs")

_INLINE_PAGE_SIZE = 10

# ─── Словарь иконок для истории активности ────────────────────────────────────
# Здесь можно напрямую менять ссылки на иконки для каждого типа события:
LOG_ICONS: dict[str, str] = {
    "new_user": "https://img.icons8.com/color/96/add-user-male.png",
    "agreement_accepted": "https://img.icons8.com/color/96/diploma.png",
    "add_city": "https://img.icons8.com/color/96/city.png",
    "change_of_city": "https://img.icons8.com/color/96/direction-signs.png",
    "add_address": "https://img.icons8.com/color/96/map-pin.png",
    "remove_address": "https://img.icons8.com/color/96/delete-sign--v1.png",
    "message_to_support": "https://img.icons8.com/color/96/technical-support.png",
    "open_support_section": "https://img.icons8.com/color/96/technical-support.png",
    "payment_request": "https://img.icons8.com/color/96/invoice.png",
    "top_up_balance": "https://img.icons8.com/color/96/bank-card-back-side.png",
    "get_check_of_top_up": "https://img.icons8.com/color/96/receipt.png",
    "get_check_of_payment_model": "https://img.icons8.com/color/96/receipt.png",
    "get_check_of_payment_private_channel": "https://img.icons8.com/color/96/receipt.png",
    "new_order": "https://img.icons8.com/color/96/shopping-bag.png",
    "open_model_form": "https://img.icons8.com/color/96/browse-folder.png",
    "promocode_activated": "https://img.icons8.com/color/96/discount--v1.png",
}
DEFAULT_LOG_ICON = "https://img.icons8.com/color/96/info--v1.png"


async def handle_log_history_inline(query: InlineQuery) -> None:
    raw_text = (query.query or "").strip()
    client_id_param = None
    search_param = None

    if "?" in raw_text:
        query_string = raw_text.split("?", 1)[1]
        qs = parse_qs(query_string)
        if "client_id" in qs and qs["client_id"]:
            client_id_param = qs["client_id"][0].strip()
        if "search" in qs and qs["search"]:
            search_param = qs["search"][0].strip()
    elif "client_id=" in raw_text:
        part = raw_text.split("client_id=", 1)[1]
        if "&" in part:
            client_id_param, remainder = part.split("&", 1)
            if "search=" in remainder:
                search_param = remainder.split("search=", 1)[1].strip()
        else:
            client_id_param = part.strip()

    if not client_id_param:
        await query.answer(
            [],
            cache_time=1,
            is_personal=True,
            switch_pm_text=t("client_log_not_specified"),
            switch_pm_parameter="start",
        )
        return

    offset_page = int(query.offset) if query.offset and query.offset.isdigit() else 1

    try:
        response = await api_client.admin.list_client_logs(
            client_id=client_id_param,
            query=search_param or None,
            page=offset_page,
            per_page=_INLINE_PAGE_SIZE,
        )

        if not response.items:
            await query.answer(
                [],
                cache_time=1,
                is_personal=True,
                switch_pm_text=t("client_log_history_empty"),
                switch_pm_parameter="start",
            )
            return

        results = []
        for log in response.items:
            created_str = format_datetime_ru(log.created_at)
            desc = f"{log.description or ''}\n{created_str}".strip()

            if log.event_type == "payment_request" and "пополнение" in (log.title or "").lower():
                thumb = LOG_ICONS.get("top_up_balance", LOG_ICONS.get("payment_request", DEFAULT_LOG_ICON))
            else:
                thumb = LOG_ICONS.get(log.event_type, DEFAULT_LOG_ICON)

            results.append(
                InlineQueryResultArticle(
                    id=f"log:{log.id}",
                    title=log.title,
                    description=desc,
                    thumbnail_url=thumb,
                    input_message_content=InputTextMessageContent(
                        message_text=f"get_log_{log.id}",
                    ),
                )
            )

        has_next = offset_page * _INLINE_PAGE_SIZE < response.total
        next_offset = str(offset_page + 1) if has_next else ""

        await query.answer(
            results=results,
            cache_time=0,
            is_personal=True,
            next_offset=next_offset,
        )
    except Exception:
        logger.exception("Error handling admin log_history inline query: %r", raw_text)
        await query.answer([], cache_time=1, is_personal=True)


@router.message(F.chat.type == "private", F.text.regexp(r"^get_log_(\d+)$"))
async def open_log_from_inline(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        log_id = int((message.text or "").rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return

    try:
        await message.delete()
    except Exception:
        pass

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

    anchor = await state.get_data()
    chat_id = anchor.get("admin_panel_chat_id") or message.chat.id
    msg_id = anchor.get("admin_panel_message_id")

    if msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                parse_mode="HTML",
                reply_markup=markup,
            )
            return
        except Exception:
            pass

    sent = await message.answer(text, parse_mode="HTML", reply_markup=markup)
    await state.update_data(admin_panel_chat_id=sent.chat.id, admin_panel_message_id=sent.message_id)
