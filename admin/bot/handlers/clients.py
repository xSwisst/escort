import logging
import math
from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from bot.assets.texts import t
from bot.keyboards import kb_agreements, kb_back, kb_client_card, kb_clients_list, kb_clients_menu
from bot.states import ClientSearchState, VASendMessage
from clients.api import ApiNotFoundError, api_client
from core.settings import settings
from services import build_client_card_text, build_client_list_text
from shared.utils.date import format_datetime_ru

logger = logging.getLogger(__name__)

router = Router(name="admin_clients")

_CLIENT_INLINE_ICON = "https://i.postimg.cc/4dcLSvhc/mamont.png"
_INLINE_PAGE_SIZE = 20


async def _store_search(state: FSMContext, *, query: str | None, page: int) -> None:
    await state.update_data(admin_clients_query=query, admin_clients_page=page)


async def _load_search(state: FSMContext) -> tuple[str | None, int]:
    data = await state.get_data()
    return data.get("admin_clients_query"), int(data.get("admin_clients_page", 1) or 1)


async def _show_clients(call: CallbackQuery, state: FSMContext, *, query: str | None, page: int) -> None:
    response = await api_client.admin.list_clients(query=query, page=page, per_page=settings.ADMIN_RESULTS_PER_PAGE)
    await _store_search(state, query=query, page=page)
    await call.message.edit_text(
        build_client_list_text(response),
        parse_mode="HTML",
        reply_markup=kb_clients_list(
            items=list(response.items),
            page=response.page,
            total=response.total,
            per_page=response.per_page,
            query=response.query,
        ),
    )
    await call.answer()


async def _show_client(call: CallbackQuery, *, user_id: int) -> None:
    client = await api_client.admin.get_client(user_id)
    await call.message.edit_text(
        build_client_card_text(client),
        parse_mode="HTML",
        reply_markup=kb_client_card(
            user_id=user_id,
            is_banned=client.is_banned,
            client_id=getattr(client, "id", None),
        ),
    )


# ── Inline Query для клиентов (my_clients) ───────────────────────────────────

@router.inline_query()
async def handle_clients_inline(query: InlineQuery) -> None:
    raw_text = (query.query or "").strip()
    if raw_text.startswith("log_history"):
        from .client_logs import handle_log_history_inline
        await handle_log_history_inline(query)
        return

    search_text = raw_text
    if "search=" in raw_text:
        search_text = raw_text.split("search=", 1)[1].strip()
    elif raw_text.startswith("my_clients"):
        search_text = raw_text[len("my_clients"):].lstrip("?").strip()
    elif raw_text.startswith("clients"):
        search_text = raw_text[len("clients"):].lstrip("?").strip()

    if search_text.startswith("search="):
        search_text = search_text[len("search="):].strip()

    offset_page = int(query.offset) if query.offset and query.offset.isdigit() else 1

    try:
        response = await api_client.admin.list_clients(
            query=search_text or None,
            page=offset_page,
            per_page=_INLINE_PAGE_SIZE,
        )

        if not response.items:
            await query.answer(
                [],
                cache_time=1,
                is_personal=True,
                switch_pm_text=t("va_client_inline_empty"),
                switch_pm_parameter="start",
            )
            return

        results = []
        for client in response.items:
            full_name = f"{client.first_name or ''} {client.last_name or ''}".strip() or "Клиент"
            username_text = f"@{client.username}" if client.username else "Без юзернейма"
            reg_date = getattr(client, "registered_at", None) or getattr(client, "created_at", None)
            created_str = format_datetime_ru(reg_date) if reg_date else "—"
            desc = f"{username_text} | {client.user_id}\nДата регистрации: {created_str}"

            results.append(
                InlineQueryResultArticle(
                    id=f"client:{client.user_id}",
                    title=full_name,
                    description=desc,
                    thumbnail_url=_CLIENT_INLINE_ICON,
                    input_message_content=InputTextMessageContent(
                        message_text=f"get_client_profile_{client.user_id}",
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
        logger.exception("Error handling admin clients inline query: %r", raw_text)
        await query.answer([], cache_time=1, is_personal=True)


@router.message(F.chat.type == "private", F.text.regexp(r"^get_client_profile_(\d+)$"))
async def open_client_from_inline(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        user_id = int((message.text or "").rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return

    try:
        await message.delete()
    except Exception:
        pass

    try:
        client = await api_client.admin.get_client(user_id)
    except Exception:
        await message.answer(t("client_not_found"))
        return

    text = build_client_card_text(client)
    markup = kb_client_card(
        user_id=user_id,
        is_banned=client.is_banned,
        client_id=getattr(client, "id", None),
    )

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


# ── Меню и поиск клиентов ───────────────────────────────────────────────────

@router.callback_query(F.data == "admin:clients:menu")
async def clients_menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(t("va_client_mgmt_caption"), parse_mode="HTML", reply_markup=kb_clients_menu())
    await call.answer()


@router.callback_query(F.data == "admin:clients:search")
async def start_search(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ClientSearchState.waiting_query)
    await call.message.edit_text(t("search_prompt"), parse_mode="HTML", reply_markup=kb_back("admin:clients:menu"))
    await call.answer()


@router.callback_query(F.data.startswith("admin:clients:recent:"))
async def recent_clients(call: CallbackQuery, state: FSMContext) -> None:
    page = int(call.data.rsplit(":", 1)[1])
    await _show_clients(call, state, query=None, page=page)


@router.callback_query(F.data.startswith("admin:clients:page:"))
async def page_clients(call: CallbackQuery, state: FSMContext) -> None:
    page = int(call.data.rsplit(":", 1)[1])
    query, _ = await _load_search(state)
    await _show_clients(call, state, query=query, page=page)


@router.callback_query(F.data == "admin:clients:back")
async def back_to_results(call: CallbackQuery, state: FSMContext) -> None:
    query, page = await _load_search(state)
    if query:
        await _show_clients(call, state, query=query, page=page)
    else:
        await clients_menu(call, state)


@router.message(ClientSearchState.waiting_query, F.chat.type == "private")
async def apply_search(message: Message, state: FSMContext) -> None:
    query = (message.text or "").strip()
    anchor = await state.get_data()
    try:
        await message.delete()
    except Exception:
        pass
    await state.clear()
    await state.update_data(
        admin_panel_chat_id=anchor.get("admin_panel_chat_id"),
        admin_panel_message_id=anchor.get("admin_panel_message_id"),
    )
    response = await api_client.admin.list_clients(query=query, page=1, per_page=settings.ADMIN_RESULTS_PER_PAGE)
    await _store_search(state, query=query, page=1)
    chat_id = anchor.get("admin_panel_chat_id") or message.chat.id
    msg_id = anchor.get("admin_panel_message_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=build_client_list_text(response),
                parse_mode="HTML",
                reply_markup=kb_clients_list(
                    items=list(response.items),
                    page=response.page,
                    total=response.total,
                    per_page=response.per_page,
                    query=response.query,
                ),
            )
            return
        except Exception:
            pass

    sent = await message.answer(
        text=build_client_list_text(response),
        parse_mode="HTML",
        reply_markup=kb_clients_list(
            items=list(response.items),
            page=response.page,
            total=response.total,
            per_page=response.per_page,
            query=response.query,
        ),
    )
    await state.update_data(admin_panel_chat_id=sent.chat.id, admin_panel_message_id=sent.message_id)


# ── /u_<id> команда ──────────────────────────────────────────────────────────

@router.message(F.text.startswith("/u_"))
async def command_search_client(message: Message, state: FSMContext, bot: Bot):
    try:
        await message.delete()
    except Exception:
        pass
    try:
        user_id = int(message.text.split("_", 1)[1])
    except (IndexError, ValueError):
        return
    try:
        client = await api_client.admin.get_client(user_id)
    except Exception:
        await message.answer(t("client_not_found"))
        return

    text = build_client_card_text(client)
    markup = kb_client_card(
        user_id=user_id,
        is_banned=client.is_banned,
        client_id=getattr(client, "id", None),
    )

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


@router.callback_query(F.data.startswith("admin:user:refresh:"))
async def refresh_client(call: CallbackQuery) -> None:
    user_id = int(call.data.rsplit(":", 1)[1])
    try:
        await _show_client(call, user_id=user_id)
    except ApiNotFoundError:
        await call.answer(t("client_not_found"), show_alert=True)
        return
    await call.answer(t("client_updated"))


@router.callback_query(F.data.startswith("admin:user:agreements:"))
async def show_agreements(call: CallbackQuery) -> None:
    user_id = int(call.data.rsplit(":", 1)[1])
    agreements = await api_client.admin.list_agreements()
    await call.message.edit_text(
        t("choose_agreement"),
        parse_mode="HTML",
        reply_markup=kb_agreements(user_id=user_id, agreements=list(agreements.items)),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:user:set-agreement:"))
async def set_agreement(call: CallbackQuery) -> None:
    _, _, _, user_id_raw, agreement_id = call.data.split(":", 4)
    user_id = int(user_id_raw)
    try:
        await api_client.admin.set_agreement(user_id=user_id, agreement_id=agreement_id)
        await _show_client(call, user_id=user_id)
    except ApiNotFoundError:
        await call.answer(t("agreement_not_found"), show_alert=True)
        return
    await call.answer(t("agreement_updated"))


@router.callback_query(F.data.startswith("admin:user:ban:"))
async def toggle_ban(call: CallbackQuery) -> None:
    user_id = int(call.data.rsplit(":", 1)[1])
    try:
        client = await api_client.admin.get_client(user_id)
        await api_client.admin.set_ban(user_id=user_id, is_banned=not client.is_banned)
        await _show_client(call, user_id=user_id)
    except ApiNotFoundError:
        await call.answer(t("client_not_found"), show_alert=True)
        return
    await call.answer(t("ban_updated"))


@router.callback_query(F.data.regexp(r"^admin:user:\d+$"))
async def open_client(call: CallbackQuery) -> None:
    user_id = int(call.data.rsplit(":", 1)[1])
    try:
        await _show_client(call, user_id=user_id)
    except ApiNotFoundError:
        await call.answer(t("client_not_found"), show_alert=True)
        return
    await call.answer()


# ── Отправка сообщения клиенту ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:user:msg:"))
async def ask_send_message(call: CallbackQuery, state: FSMContext) -> None:
    user_id = int(call.data.split(":")[3])
    await state.update_data(
        msg_target_user_id=user_id,
        msg_bot_msg_id=call.message.message_id,
        msg_bot_chat_id=call.message.chat.id,
    )
    await state.set_state(VASendMessage.text)
    await call.message.edit_text(t("send_message_prompt"), parse_mode="HTML", reply_markup=kb_back(f"admin:user:{user_id}"))
    await call.answer()


@router.message(StateFilter(VASendMessage.text), F.chat.type == "private")
async def process_send_message(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    user_id = int(data.get("msg_target_user_id") or 0)
    text = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not user_id or not text:
        return

    from bot.keyboards.clients import approve_send_message_ikb

    await state.update_data(msg_text=text)
    bot_msg_id = data.get("msg_bot_msg_id")
    chat_id = data.get("msg_bot_chat_id") or message.chat.id

    if bot_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=t("send_message_confirm", text=text),
                parse_mode="HTML",
                reply_markup=approve_send_message_ikb(user_id),
            )
            return
        except Exception:
            pass

    sent = await message.answer(
        t("send_message_confirm", text=text),
        parse_mode="HTML",
        reply_markup=approve_send_message_ikb(user_id),
    )
    await state.update_data(msg_bot_msg_id=sent.message_id)


@router.callback_query(F.data == "admin:user:msg:approve")
async def approve_send_message(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = int(data.get("msg_target_user_id") or 0)
    text = data.get("msg_text")
    await state.clear()
    if not user_id or not text:
        return

    try:
        await api_client.admin.send_message_to_client(user_id=user_id, text=text)
        await call.answer(t("send_message_success"), show_alert=True)
    except Exception:
        await call.answer(t("send_message_fail"), show_alert=True)

    try:
        await _show_client(call, user_id=user_id)
    except Exception:
        pass


