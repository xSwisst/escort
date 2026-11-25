from __future__ import annotations

import logging
from typing import Any

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.texts import t
from bot.keyboards import (
    build_malling_inline_keyboard,
    kb_malling_audience,
    kb_malling_back_settings,
    kb_malling_button_confirm,
    kb_malling_button_delete_confirm,
    kb_malling_button_type,
    kb_malling_button_view,
    kb_malling_buttons_list,
    kb_malling_cancel,
    kb_malling_hide,
    kb_malling_media_confirm,
    kb_malling_settings,
)
from bot.states import VAMalling
from clients.api import api_client
from .panel import edit_panel

router = Router(name="admin_malling")
logger = logging.getLogger(__name__)


def _render_settings_text(data: dict[str, Any]) -> str:
    audience_map = {
        "all": t("va_malling_audience_all_short"),
        "new7": t("va_malling_audience_7d_short"),
        "new14": t("va_malling_audience_14d_short"),
        "new30": t("va_malling_audience_30d_short"),
    }
    source_ready = bool((data.get("malling_text") or "").strip())
    media_ready = bool(data.get("malling_media"))
    buttons_ready = bool(data.get("malling_buttons"))
    return t(
        "va_malling_settings",
        audience=audience_map.get(data.get("malling_audience", "all"), "—"),
        content_status=t("word_yes") if source_ready else t("word_no"),
        media_status=t("word_yes") if media_ready else t("word_no"),
        buttons_status=t("word_yes") if buttons_ready else t("word_no"),
    )


@router.callback_query(F.data == "admin:malling:menu")
@router.callback_query(F.data == "admin:malling:audience")
async def ask_audience(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VAMalling.audience)
    await state.update_data(
        va_message_id=call.message.message_id,
        malling_buttons=[],
        malling_media=None,
        malling_text=None,
    )
    await call.message.edit_text(
        t("va_malling_audience_prompt"),
        parse_mode="HTML",
        reply_markup=kb_malling_audience(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:malling:aud:"), StateFilter(VAMalling.audience))
async def select_audience(call: CallbackQuery, state: FSMContext) -> None:
    aud = call.data.split(":")[3]
    if aud not in {"all", "new7", "new14", "new30"}:
        await call.answer(t("va_answer_error"), show_alert=True)
        return
    await state.update_data(malling_audience=aud)
    await state.set_state(VAMalling.message)
    await call.message.edit_text(
        t("va_malling_enter"),
        parse_mode="HTML",
        reply_markup=kb_malling_cancel(),
    )
    await call.answer()


@router.message(StateFilter(VAMalling.message), F.chat.type == "private")
async def process_malling_message(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    text = (message.text or message.caption or "").strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not text:
        return
    await state.update_data(malling_text=text)
    await state.set_state(VAMalling.settings)
    updated_data = await state.get_data()
    msg_id = data.get("va_message_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=_render_settings_text(updated_data),
                parse_mode="HTML",
                reply_markup=kb_malling_settings(),
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        _render_settings_text(updated_data),
        parse_mode="HTML",
        reply_markup=kb_malling_settings(),
    )
    await state.update_data(va_message_id=sent.message_id)


@router.callback_query(F.data == "admin:malling:settings")
async def show_settings(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(VAMalling.settings)
    await call.message.edit_text(
        _render_settings_text(data),
        parse_mode="HTML",
        reply_markup=kb_malling_settings(),
    )
    await call.answer()


@router.callback_query(F.data == "admin:malling:cancel")
async def cancel_malling(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await edit_panel(call, state)


@router.callback_query(F.data == "admin:malling:media:add", StateFilter(VAMalling.settings))
async def ask_media(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VAMalling.add_media)
    await call.message.edit_text(
        t("va_malling_media_prompt"),
        parse_mode="HTML",
        reply_markup=kb_malling_back_settings(),
    )
    await call.answer()


@router.message(StateFilter(VAMalling.add_media), F.chat.type == "private")
async def process_media(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    msg_id = data.get("va_message_id")
    media_url: str | None = None

    if message.photo:
        media_url = message.photo[-1].file_id
    elif message.text:
        text = message.text.strip()
        if text.startswith(("http://", "https://")):
            media_url = text

    try:
        await message.delete()
    except Exception:
        pass

    if not media_url:
        if msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=msg_id,
                    text=t("va_malling_media_invalid"),
                    parse_mode="HTML",
                    reply_markup=kb_malling_back_settings(),
                )
                return
            except Exception:
                pass
        await message.answer(
            t("va_malling_media_invalid"),
            parse_mode="HTML",
            reply_markup=kb_malling_back_settings(),
        )
        return

    await state.update_data(va_pending_media_url=media_url)
    await state.set_state(VAMalling.add_media_confirm)
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=t("va_malling_media_confirm"),
                parse_mode="HTML",
                reply_markup=kb_malling_media_confirm(),
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        t("va_malling_media_confirm"),
        parse_mode="HTML",
        reply_markup=kb_malling_media_confirm(),
    )
    await state.update_data(va_message_id=sent.message_id)


@router.callback_query(F.data == "admin:malling:media:confirm", StateFilter(VAMalling.add_media_confirm))
async def confirm_media(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    media_url = data.get("va_pending_media_url")
    if not media_url:
        await call.answer(t("va_answer_error"), show_alert=True)
        return
    await state.update_data(malling_media=media_url, va_pending_media_url=None)
    await show_settings(call, state)
    await call.answer(t("va_answer_updated"))


@router.callback_query(F.data == "admin:malling:buttons", StateFilter(VAMalling.settings))
@router.callback_query(F.data.startswith("admin:malling:buttons:page:"), StateFilter(VAMalling.settings))
async def show_buttons(call: CallbackQuery, state: FSMContext) -> None:
    page = 1
    if call.data.startswith("admin:malling:buttons:page:"):
        page = int(call.data.split(":")[4])
    data = await state.get_data()
    buttons_data = list(data.get("malling_buttons") or [])
    await call.message.edit_text(
        t("va_malling_buttons_title"),
        parse_mode="HTML",
        reply_markup=kb_malling_buttons_list(buttons_data, page=page),
    )
    await call.answer()


@router.callback_query(F.data == "admin:malling:btn:add", StateFilter(VAMalling.settings))
async def ask_button_type(call: CallbackQuery) -> None:
    await call.message.edit_text(
        t("va_malling_button_type_prompt"),
        parse_mode="HTML",
        reply_markup=kb_malling_button_type(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:malling:btn:type:"), StateFilter(VAMalling.settings))
async def select_button_type(call: CallbackQuery, state: FSMContext) -> None:
    btype = call.data.split(":")[4]
    if btype not in {"url", "callback", "copy"}:
        await call.answer(t("va_answer_error"), show_alert=True)
        return
    await state.update_data(va_pending_button_type=btype)
    await state.set_state(VAMalling.button_text)
    await call.message.edit_text(
        t("va_malling_button_text_prompt"),
        parse_mode="HTML",
        reply_markup=kb_malling_back_settings(),
    )
    await call.answer()


@router.message(StateFilter(VAMalling.button_text), F.chat.type == "private")
async def process_button_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    text = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not text:
        return
    btype = data.get("va_pending_button_type", "url")
    prompt_map = {
        "url": "va_malling_button_value_url_prompt",
        "callback": "va_malling_button_value_callback_prompt",
        "copy": "va_malling_button_value_copy_prompt",
    }
    prompt_key = prompt_map.get(btype, "va_malling_button_value_url_prompt")
    await state.update_data(va_pending_button_text=text)
    await state.set_state(VAMalling.button_value)
    msg_id = data.get("va_message_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=t(prompt_key),
                parse_mode="HTML",
                reply_markup=kb_malling_back_settings(),
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        t(prompt_key),
        parse_mode="HTML",
        reply_markup=kb_malling_back_settings(),
    )
    await state.update_data(va_message_id=sent.message_id)


@router.message(StateFilter(VAMalling.button_value), F.chat.type == "private")
async def process_button_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    val = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not val:
        return
    await state.update_data(va_pending_button_value=val)
    await state.set_state(VAMalling.button_confirm)
    msg_id = data.get("va_message_id")
    confirm_text = t(
        "va_malling_button_confirm",
        button_type=data.get("va_pending_button_type", "url"),
        button_text=data.get("va_pending_button_text", "—"),
        button_value=val,
    )
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=confirm_text,
                parse_mode="HTML",
                reply_markup=kb_malling_button_confirm(),
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        confirm_text,
        parse_mode="HTML",
        reply_markup=kb_malling_button_confirm(),
    )
    await state.update_data(va_message_id=sent.message_id)


@router.callback_query(F.data == "admin:malling:btn:add:confirm", StateFilter(VAMalling.button_confirm))
async def confirm_add_button(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    btype = data.get("va_pending_button_type")
    btext = (data.get("va_pending_button_text") or "").strip()
    bval = (data.get("va_pending_button_value") or "").strip()
    if not btype or not btext or not bval:
        await call.answer(t("va_answer_error"), show_alert=True)
        return
    btns = list(data.get("malling_buttons") or [])
    if btype == "url":
        btns.append({"type": "url", "text": btext, "url": bval})
    elif btype == "copy":
        btns.append({"type": "copy", "text": btext, "copy_text": bval})
    else:
        btns.append({"type": "callback", "text": btext, "callback_data": bval[:64]})
    await state.update_data(
        malling_buttons=btns,
        va_pending_button_type=None,
        va_pending_button_text=None,
        va_pending_button_value=None,
    )
    await show_settings(call, state)
    await call.answer(t("va_answer_updated"))


@router.callback_query(F.data.startswith("admin:malling:btn:view:"))
async def view_button(call: CallbackQuery, state: FSMContext) -> None:
    idx = int(call.data.split(":")[4])
    data = await state.get_data()
    btns = list(data.get("malling_buttons") or [])
    if idx < 0 or idx >= len(btns):
        await call.answer(t("va_answer_error"), show_alert=True)
        return
    item = btns[idx]
    val = item.get("url") or item.get("callback_data") or item.get("copy_text") or "—"
    await call.message.edit_text(
        t(
            "va_malling_button_view",
            index=idx + 1,
            button_type=item.get("type", "url"),
            button_text=item.get("text", "—"),
            button_value=val,
        ),
        parse_mode="HTML",
        reply_markup=kb_malling_button_view(idx),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:malling:btn:del:confirm:"))
async def confirm_delete_button(call: CallbackQuery, state: FSMContext) -> None:
    idx = int(call.data.split(":")[5])
    data = await state.get_data()
    btns = list(data.get("malling_buttons") or [])
    if idx < 0 or idx >= len(btns):
        await call.answer(t("va_answer_error"), show_alert=True)
        return
    btns.pop(idx)
    await state.update_data(malling_buttons=btns)
    await call.message.edit_text(
        t("va_malling_buttons_title"),
        parse_mode="HTML",
        reply_markup=kb_malling_buttons_list(btns),
    )
    await call.answer(t("va_answer_deleted"))


@router.callback_query(F.data.startswith("admin:malling:btn:del:"))
async def prompt_delete_button(call: CallbackQuery, state: FSMContext) -> None:
    idx = int(call.data.split(":")[4])
    data = await state.get_data()
    btns = list(data.get("malling_buttons") or [])
    if idx < 0 or idx >= len(btns):
        await call.answer(t("va_answer_error"), show_alert=True)
        return
    await call.message.edit_text(
        t("va_malling_button_delete_confirm", text=btns[idx].get("text", "—")),
        parse_mode="HTML",
        reply_markup=kb_malling_button_delete_confirm(idx),
    )
    await call.answer()


@router.callback_query(F.data == "admin:malling:preview", StateFilter(VAMalling.settings))
async def preview_malling(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text = data.get("malling_text") or ""
    media = data.get("malling_media")
    btns = list(data.get("malling_buttons") or [])
    if not text:
        await call.answer(t("va_answer_error"), show_alert=True)
        return

    preview_kb = build_malling_inline_keyboard(btns)
    hide_kb = kb_malling_hide()
    if preview_kb:
        rows = list(preview_kb.inline_keyboard)
        rows.append(hide_kb.inline_keyboard[0])
        preview_markup = type(preview_kb)(inline_keyboard=rows)
    else:
        preview_markup = hide_kb

    try:
        if media:
            await call.message.answer_photo(
                photo=media,
                caption=text,
                parse_mode="HTML",
                reply_markup=preview_markup,
            )
        else:
            await call.message.answer(
                text=text,
                parse_mode="HTML",
                reply_markup=preview_markup,
            )
        await call.answer(t("va_malling_preview_ready"))
    except Exception as exc:
        await call.answer(f"Ошибка предпросмотра: {exc}", show_alert=True)


@router.callback_query(F.data == "admin:malling:send", StateFilter(VAMalling.settings))
async def send_malling(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text = (data.get("malling_text") or "").strip()
    if not text:
        await call.answer("Сначала введите текст рассылки", show_alert=True)
        return

    audience = data.get("malling_audience", "all")
    media = data.get("malling_media")
    btns = list(data.get("malling_buttons") or [])

    # Filter out buttons with None url if sending to broadcast endpoint
    valid_btns = []
    for b in btns:
        if b.get("url"):
            valid_btns.append({"text": b["text"], "url": b["url"]})

    admin = await api_client.admin.get_or_create_admin(
        call.from_user.id,
        username=call.from_user.username,
        first_name=call.from_user.first_name,
        last_name=call.from_user.last_name,
    )

    payload = {
        "admin_id": admin.id,
        "audience": audience,
        "text": text,
        "media_url": media,
        "buttons": valid_btns,
    }

    await call.answer(t("va_malling_started_answer"))
    try:
        result = await api_client.admin.start_broadcast(payload)
        sent = result.sent
        failed = result.failed
        total = result.total
    except Exception as exc:
        logger.exception("Broadcast failed: %s", exc)
        sent = 0
        failed = 0
        total = 0

    await state.clear()
    report = t("va_malling_done", sent=sent, total=total, failed=failed)

    try:
        from bot.services.logs import emit_admin_info
        await emit_admin_info(
            event_type="mailing",
            payload={
                "audience": audience,
                "total": total,
                "sent": sent,
                "failed": failed,
                "text": text,
            },
            actor_id=call.from_user.id,
        )
    except Exception:
        pass

    await call.message.answer(report, parse_mode="HTML", reply_markup=kb_malling_hide())
    await edit_panel(call, state)



@router.callback_query(F.data == "admin:malling:hide")
async def hide_malling(call: CallbackQuery) -> None:
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.answer()

