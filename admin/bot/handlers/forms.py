from __future__ import annotations

import asyncio
import io
import logging
from datetime import datetime
from typing import Any

import httpx
from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.assets.texts import t
from bot.keyboards import (
    kb_additionals_list,
    kb_approve_new_model,
    kb_back,
    kb_confirm_delete_model,
    kb_edit_params,
    kb_form_photos,
    kb_model_card,
    kb_models_list,
    kb_param_confirm_delete,
    kb_param_confirm_update,
    kb_param_input,
    kb_positions,
    kb_review_card,
    kb_reviews_list,
    kb_services_list,
)
from bot.states import (
    VAAddPhoto,
    VAEditAdditional,
    VAEditParam,
    VAEditReview,
    VAEditService,
    VANewAdditional,
    VANewModel,
    VANewReview,
    VANewService,
)
from clients.api import ApiNotFoundError, api_client


async def _resolve_admin_id(tg_user) -> int:
    admin = await api_client.admin.get_or_create_admin(
        tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )
    return admin.id


async def _resolve_admin_id_by_tg(user_id: int) -> int:
    admin = await api_client.admin.get_or_create_admin(user_id)
    return admin.id
from bot.services import build_model_card_text

router = Router(name="admin_forms")
logger = logging.getLogger(__name__)

PHOTOS_INTERNAL_URL = "http://photos:8005"

_album_buffers: dict[int, dict] = {}
_ALBUM_BUFFER_TTL = 120

MIN_MODEL_PRICE = 1_000
MAX_MODEL_PRICE = 1_000_000


async def _fetch_photo_bytes(storage_key: str) -> bytes | None:
    if not storage_key:
        return None
    cleaned = storage_key.strip()
    urls_to_try = []
    if "/c/" in cleaned:
        path = cleaned.split("/c/", 1)[1]
        urls_to_try.append(f"{PHOTOS_INTERNAL_URL}/c/{path}")
    elif cleaned.startswith("http://") or cleaned.startswith("https://"):
        urls_to_try.append(cleaned)
    else:
        urls_to_try.append(f"{PHOTOS_INTERNAL_URL}/c/{cleaned.lstrip('/')}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in urls_to_try:
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and resp.content:
                    return resp.content
            except Exception:
                continue
    return None


async def _render_text_menu(call: CallbackQuery, text: str, reply_markup=None) -> None:
    """Safely edits text menu, deleting previous photo message if any."""
    if call.message.photo:
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer(text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        try:
            await call.message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
        except Exception as exc:
            if "message is not modified" in str(exc).lower():
                return
            try:
                await call.message.delete()
            except Exception:
                pass
            await call.message.answer(text, parse_mode="HTML", reply_markup=reply_markup)


# ── Список анкет ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:forms:city")
async def choose_city(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    call.data = "admin:forms:city:1:1"
    await show_forms_list(call, state)


@router.callback_query(F.data.startswith("admin:forms:city:"))
async def show_forms_list(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    city_slot = 1
    page = int(parts[4]) if len(parts) > 4 else 1

    admin_id = await _resolve_admin_id(call.from_user)
    forms_resp = await api_client.admin.list_forms(city_slot=city_slot, admin_id=admin_id)
    forms = forms_resp.items
    total = len(forms)
    total_pages = max(1, (total + 5) // 6)

    text = t("models_list_caption", city_slot=city_slot, total=total, page=page, total_pages=total_pages)
    if total == 0:
        text = t("models_list_empty")

    await _render_text_menu(call, text, reply_markup=kb_models_list(forms, city_slot, page=page))
    await call.answer()


# ── Просмотр карточки анкеты ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:form:info:"))
async def show_model_card(call: CallbackQuery, state: FSMContext, code: str | None = None) -> None:
    if not code:
        code = call.data.split(":")[3]
    try:
        admin_id = await _resolve_admin_id(call.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
    except ApiNotFoundError:
        await call.answer("Анкета не найдена", show_alert=True)
        return

    text = build_model_card_text(form)
    kb = kb_model_card(form, form.city_slot)
    await _render_text_menu(call, text, reply_markup=kb)
    await call.answer()


# ── Создание новой анкеты (Мастер FSM) ────────────────────────────────────────

@router.callback_query(F.data.regexp(r"^admin:forms:new:(\d+)$"))
async def new_model_start(call: CallbackQuery, state: FSMContext) -> None:
    city_slot = int(call.data.split(":")[3])
    await state.clear()
    await state.update_data(
        new_form_city_slot=city_slot,
        new_form_photos=[],
        va_message_id=call.message.message_id,
        va_chat_id=call.message.chat.id,
    )
    await state.set_state(VANewModel.params)
    await _render_text_menu(
        call,
        t("models_new_step1"),
        reply_markup=kb_back(f"admin:forms:city:{city_slot}:1"),
    )
    await call.answer()


@router.message(StateFilter(VANewModel.params), F.chat.type == "private")
async def new_model_step1_params(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    data = await state.get_data()
    city_slot = int(data.get("new_form_city_slot") or 1)
    bot_msg_id = data.get("va_message_id")
    chat_id = data.get("va_chat_id") or message.chat.id
    back_markup = kb_back(f"admin:forms:city:{city_slot}:1")

    text = (message.text or "").strip()
    parts = text.split()
    if len(parts) != 4 or not parts[1].isdigit() or not parts[2].isdigit() or not parts[3].isdigit():
        if bot_msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=t("models_new_step1_invalid"),
                    parse_mode="HTML",
                    reply_markup=back_markup,
                )
                return
            except Exception:
                pass
        sent = await message.answer(t("models_new_step1_invalid"), parse_mode="HTML", reply_markup=back_markup)
        await state.update_data(va_message_id=sent.message_id)
        return

    name = parts[0]
    age = int(parts[1])
    height = int(parts[2])
    bust_size = int(parts[3])

    if not (18 <= age <= 99) or not (140 <= height <= 220) or not (0 <= bust_size <= 10):
        if bot_msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=t("models_new_step1_invalid"),
                    parse_mode="HTML",
                    reply_markup=back_markup,
                )
                return
            except Exception:
                pass
        sent = await message.answer(t("models_new_step1_invalid"), parse_mode="HTML", reply_markup=back_markup)
        await state.update_data(va_message_id=sent.message_id)
        return

    await state.update_data(
        new_form_name=name,
        new_form_age=age,
        new_form_height=height,
        new_form_bust_size=bust_size,
    )
    await state.set_state(VANewModel.prices)
    if bot_msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=t("models_new_step2"),
                parse_mode="HTML",
                reply_markup=back_markup,
            )
            return
        except Exception:
            pass
    sent = await message.answer(t("models_new_step2"), parse_mode="HTML", reply_markup=back_markup)
    await state.update_data(va_message_id=sent.message_id)


@router.message(StateFilter(VANewModel.prices), F.chat.type == "private")
async def new_model_step2_prices(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    data = await state.get_data()
    city_slot = int(data.get("new_form_city_slot") or 1)
    bot_msg_id = data.get("va_message_id")
    chat_id = data.get("va_chat_id") or message.chat.id
    back_markup = kb_back(f"admin:forms:city:{city_slot}:1")

    text = (message.text or "").strip()
    parts = text.split()
    if len(parts) != 4 or not all(p.isdigit() for p in parts):
        err_msg = t("models_new_step2_invalid")
        if bot_msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=f"{err_msg}\n\n{t('models_new_step2')}",
                    parse_mode="HTML",
                    reply_markup=back_markup,
                )
                return
            except Exception:
                pass
        sent = await message.answer(f"{err_msg}\n\n{t('models_new_step2')}", parse_mode="HTML", reply_markup=back_markup)
        await state.update_data(va_message_id=sent.message_id)
        return

    prices = [int(p) for p in parts]
    if any(p < MIN_MODEL_PRICE or p > MAX_MODEL_PRICE for p in prices):
        err_msg = (
            f"❗️ <b>Ошибка!</b> Цены должны быть от <b>{MIN_MODEL_PRICE:,} RUB</b> "
            f"до <b>{MAX_MODEL_PRICE:,} RUB</b>.\nПожалуйста, повторите попытку:"
        ).replace(",", " ")
        if bot_msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=f"{err_msg}\n\n{t('models_new_step2')}",
                    parse_mode="HTML",
                    reply_markup=back_markup,
                )
                return
            except Exception:
                pass
        sent = await message.answer(f"{err_msg}\n\n{t('models_new_step2')}", parse_mode="HTML", reply_markup=back_markup)
        await state.update_data(va_message_id=sent.message_id)
        return

    p1, p2, p3, p_night = prices
    await state.update_data(
        new_form_price_1h=p1,
        new_form_price_2h=p2,
        new_form_price_3h=p3,
        new_form_price_night=p_night,
    )
    await state.set_state(VANewModel.photos)
    if bot_msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=t("models_new_step3"),
                parse_mode="HTML",
                reply_markup=back_markup,
            )
            return
        except Exception:
            pass
    sent = await message.answer(
        t("models_new_step3"),
        parse_mode="HTML",
        reply_markup=back_markup,
    )
    await state.update_data(va_message_id=sent.message_id)


# ── Сбор медиа/альбомов (Debounce Buffer) ─────────────────────────────────────

async def _flush_new_album(user_id: int, bot: Bot, state: FSMContext):
    await asyncio.sleep(0.8)
    buf = _album_buffers.pop(user_id, None)
    if not buf:
        return
    for mid in buf.get("msg_ids", []):
        try:
            await bot.delete_message(user_id, mid)
        except Exception:
            pass

    items = buf.get("items", [])[:20]
    data = await state.get_data()
    photos_data = list(data.get("new_form_photos") or [])

    for item in items:
        fid = item["fid"]
        try:
            file_io = io.BytesIO()
            await bot.download(fid, destination=file_io)
            photos_data.append(file_io.getvalue())
        except Exception:
            logger.exception("Failed to download photo %s", fid)

    if not photos_data:
        return

    await state.update_data(new_form_photos=photos_data)
    city_slot = int(data.get("new_form_city_slot") or 1)
    bot_msg_id = data.get("va_message_id")
    chat_id = data.get("va_chat_id") or user_id

    confirm_text = t(
        "models_new_confirm",
        name=data.get("new_form_name", "—"),
        age=data.get("new_form_age", "—"),
        height=data.get("new_form_height", "—"),
        bust_size=data.get("new_form_bust_size", "—"),
        city_slot=city_slot,
        price_1h=data.get("new_form_price_1h", 0),
        price_2h=data.get("new_form_price_2h", 0),
        price_3h=data.get("new_form_price_3h", 0),
        price_night=data.get("new_form_price_night", 0),
        photos_count=len(photos_data),
    )
    markup = kb_approve_new_model(city_slot)

    if bot_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=confirm_text,
                parse_mode="HTML",
                reply_markup=markup,
            )
            return
        except Exception:
            pass

    sent = await bot.send_message(
        chat_id=chat_id,
        text=confirm_text,
        parse_mode="HTML",
        reply_markup=markup,
    )
    await state.update_data(va_message_id=sent.message_id)


async def _buffer_media(user_id: int, file_id: str, message: Message, bot: Bot, state: FSMContext, flush_fn):
    now = asyncio.get_event_loop().time()
    stale = [uid for uid, b in _album_buffers.items() if (now - b.get("created", 0)) > _ALBUM_BUFFER_TTL]
    for uid in stale:
        buf = _album_buffers.pop(uid, None)
        if buf and buf.get("task") and not buf["task"].done():
            buf["task"].cancel()

    if user_id not in _album_buffers:
        _album_buffers[user_id] = {"items": [], "msg_ids": [], "task": None, "created": now}

    buf = _album_buffers[user_id]
    buf["items"].append({"fid": file_id})
    buf["msg_ids"].append(message.message_id)

    if buf["task"] and not buf["task"].done():
        buf["task"].cancel()

    buf["task"] = asyncio.get_event_loop().create_task(flush_fn(user_id, bot, state))


@router.message(StateFilter(VANewModel.photos), F.photo)
async def new_model_step3_photo(message: Message, state: FSMContext) -> None:
    fid = message.photo[-1].file_id
    await _buffer_media(message.from_user.id, fid, message, message.bot, state, _flush_new_album)


@router.message(StateFilter(VANewModel.photos), F.document)
async def new_model_step3_doc(message: Message, state: FSMContext) -> None:
    if message.document and (message.document.mime_type or "").startswith("image/"):
        fid = message.document.file_id
        await _buffer_media(message.from_user.id, fid, message, message.bot, state, _flush_new_album)
    else:
        try:
            await message.delete()
        except Exception:
            pass


@router.message(StateFilter(VANewModel.photos))
async def new_model_step3_other(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass


@router.callback_query(F.data == "admin:forms:new:approve", StateFilter(VANewModel.photos))
async def new_model_approve(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    city_slot = int(data.get("new_form_city_slot") or 1)

    raw_photos = data.get("new_form_photos") or []
    if not raw_photos:
        await call.answer("❗️ Сначала отправьте хотя бы 1 фотографию", show_alert=True)
        return

    form_data = {
        "name": data["new_form_name"],
        "age": data["new_form_age"],
        "height": data["new_form_height"],
        "bust_size": data["new_form_bust_size"],
        "one_hour_price": data["new_form_price_1h"],
        "two_hour_price": data["new_form_price_2h"],
        "three_hour_price": data["new_form_price_3h"],
        "overnight_price": data["new_form_price_night"],
        "city_slot": city_slot,
        "is_visible": True,
    }

    files = [("files", (f"photo_{i}.jpg", b_data, "image/jpeg")) for i, b_data in enumerate(raw_photos)]

    await call.answer("Создание анкеты...")
    try:
        admin_id = await _resolve_admin_id(call.from_user)
        created = await api_client.admin.create_form(form_data, files=files if files else None, admin_id=admin_id)
        await state.clear()
        await show_model_card(call, state, code=created.code)
    except Exception as exc:
        logger.exception("Failed to create form: %s", exc)
        await call.message.answer(f"❌ Ошибка при создании анкеты: {exc}")


# ── Переключатели статусов (Toggles) ──────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:form:toggle:"))
async def toggle_model_field(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    code = parts[3]
    field = parts[4]

    try:
        admin_id = await _resolve_admin_id(call.from_user)
        await api_client.admin.toggle_form_field(code, field, admin_id=admin_id)
        await call.answer(t("model_toggled"))
        await show_model_card(call, state, code=code)
    except Exception as exc:
        await call.answer(f"Ошибка: {exc}", show_alert=True)


# ── Редактирование параметров ─────────────────────────────────────────────────

_EXTRA_PARAMS = {"rating", "caption", "orders", "channel"}
_DEFAULT_PARAMS = {"name", "age", "height", "bust_size", "one_hour_price", "two_hour_price", "three_hour_price", "overnight_price"}

_PROMPT_KEYS = {
    "name": "va_model_edit_param_name",
    "age": "va_model_edit_param_age",
    "height": "va_model_edit_param_height",
    "bust_size": "va_model_edit_param_tits",
    "one_hour_price": "va_model_edit_param_price1",
    "two_hour_price": "va_model_edit_param_price_two_hours",
    "three_hour_price": "va_model_edit_param_price2",
    "overnight_price": "va_model_edit_param_price3",
    "caption": "va_model_edit_param_caption",
    "rating": "va_model_edit_param_rating",
    "orders": "va_model_edit_param_orders",
    "channel": "va_model_edit_param_channel",
}

_CONFIRM_KEYS = {
    "name": "va_model_confirm_update_name",
    "age": "va_model_confirm_update_age",
    "height": "va_model_confirm_update_height",
    "bust_size": "va_model_confirm_update_tits",
    "one_hour_price": "va_model_confirm_update_price1",
    "two_hour_price": "va_model_confirm_update_price_two_hours",
    "three_hour_price": "va_model_confirm_update_price2",
    "overnight_price": "va_model_confirm_update_price3",
    "caption": "va_model_confirm_update_caption",
    "rating": "va_model_confirm_update_rating",
    "orders": "va_model_confirm_update_orders",
    "channel": "va_model_confirm_update_channel",
}

_DELETE_CONFIRM_KEYS = {
    "caption": "va_model_confirm_delete_caption",
    "rating": "va_model_confirm_delete_rating",
    "orders": "va_model_confirm_delete_orders",
    "channel": "va_model_confirm_delete_channel",
    "one_hour_price": "va_model_confirm_delete_price1",
    "two_hour_price": "va_model_confirm_delete_price_two_hours",
    "three_hour_price": "va_model_confirm_delete_price2",
    "overnight_price": "va_model_confirm_delete_price3",
}


def _can_delete_param(form: Any, param_name: str) -> bool:
    if not form:
        return False
    if param_name == "rating":
        return form.rating is not None and float(form.rating) > 0
    if param_name == "orders":
        return form.orders is not None and int(form.orders) > 0
    if param_name == "channel":
        return bool(str(form.public_channel_url or "").strip())
    if param_name == "caption":
        return bool(str(form.caption or "").strip())
    if param_name == "one_hour_price":
        return form.one_hour_price is not None and int(form.one_hour_price) > 0
    if param_name == "two_hour_price":
        return form.two_hour_price is not None and int(form.two_hour_price) > 0
    if param_name == "three_hour_price":
        return form.three_hour_price is not None and int(form.three_hour_price) > 0
    if param_name == "overnight_price":
        return form.overnight_price is not None and int(form.overnight_price) > 0
    return False


@router.callback_query(F.data.startswith("admin:form:edit:"))
async def edit_model_params_menu(call: CallbackQuery) -> None:
    code = call.data.split(":")[3]
    def _format_price(val: int | None) -> str:
        return f"{val} ₽" if val is not None else "—"

    try:
        admin_id = await _resolve_admin_id(call.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
        text = t(
            "va_model_edit_info",
            name=form.name,
            city=f"Город {form.city_slot}",
            age=form.age,
            tits=form.bust_size,
            price_one_hours=_format_price(form.one_hour_price),
            price_two_hours=_format_price(form.two_hour_price),
            price_three_hours=_format_price(form.three_hour_price),
            price_night=_format_price(form.overnight_price),
        )
    except Exception:
        text = "<blockquote><b>📝 Редактирование анкеты</b></blockquote>\n\nВыберите параметр для изменения:"

    await _render_text_menu(call, text, reply_markup=kb_edit_params(code))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:param:"))
async def ask_edit_param(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    code = parts[3]
    param_name = parts[4]

    try:
        admin_id = await _resolve_admin_id(call.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
    except ApiNotFoundError:
        await call.answer("Анкета не найдена", show_alert=True)
        return

    is_default = param_name in _DEFAULT_PARAMS
    can_delete = _can_delete_param(form, param_name)
    back_target = f"admin:form:edit:{code}" if is_default else f"admin:form:info:{code}"

    await state.update_data(
        edit_model_code=code,
        edit_param_name=param_name,
        edit_bot_msg_id=call.message.message_id,
        edit_bot_chat_id=call.message.chat.id,
        edit_is_default=is_default,
        edit_can_delete=can_delete,
        edit_back_target=back_target,
    )
    await state.set_state(VAEditParam.value)

    prompt = t(_PROMPT_KEYS.get(param_name, "va_model_edit_param_name"))
    await _render_text_menu(
        call,
        prompt,
        reply_markup=kb_param_input(code, param_name, can_delete=can_delete, back_target=back_target),
    )
    await call.answer()


@router.message(StateFilter(VAEditParam.value), F.chat.type == "private")
async def process_edit_param(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    code = data.get("edit_model_code")
    param_name = data.get("edit_param_name")
    bot_msg_id = data.get("edit_bot_msg_id")
    chat_id = data.get("edit_bot_chat_id") or message.chat.id
    can_delete = data.get("edit_can_delete", False)
    back_target = data.get("edit_back_target", f"admin:form:info:{code}")
    raw_val = (message.text or "").strip()

    try:
        await message.delete()
    except Exception:
        pass

    if not code or not param_name or not bot_msg_id:
        return

    input_kb = kb_param_input(code, param_name, can_delete=can_delete, back_target=back_target)
    err_text = t("va_model_wrong_format")
    prompt_text = t(_PROMPT_KEYS.get(param_name, "va_model_edit_param_name"))

    async def _send_err():
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=f"{err_text}\n\n{prompt_text}",
                parse_mode="HTML",
                reply_markup=input_kb,
            )
        except Exception:
            pass

    parsed_value: Any = raw_val
    formatted_value: str = raw_val

    if param_name in {"age", "height", "bust_size", "one_hour_price", "two_hour_price", "three_hour_price", "overnight_price", "orders"}:
        if not raw_val.isdigit() or int(raw_val) < 0:
            await _send_err()
            return
        parsed_value = int(raw_val)
        if param_name in {"one_hour_price", "two_hour_price", "three_hour_price", "overnight_price"}:
            if parsed_value < MIN_MODEL_PRICE or parsed_value > MAX_MODEL_PRICE:
                limit_err = (
                    f"❗️ <b>Ошибка!</b> Цена должна быть от <b>{MIN_MODEL_PRICE:,} RUB</b> "
                    f"до <b>{MAX_MODEL_PRICE:,} RUB</b>.\nПожалуйста, повторите попытку:"
                ).replace(",", " ")
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=bot_msg_id,
                        text=f"{limit_err}\n\n{prompt_text}",
                        parse_mode="HTML",
                        reply_markup=input_kb,
                    )
                except Exception:
                    pass
                return
        formatted_value = str(parsed_value)
    elif param_name == "rating":
        try:
            rating_val = float(raw_val.replace(",", "."))
            if not (0.0 <= rating_val <= 5.0):
                raise ValueError()
            parsed_value = rating_val
            formatted_value = f"{rating_val:.1f}"
        except ValueError:
            await _send_err()
            return
    elif param_name == "name":
        if len(raw_val) < 2:
            await _send_err()
            return
    elif param_name == "caption":
        if len(raw_val) < 2:
            await _send_err()
            return
    elif param_name == "channel":
        if not any(p in raw_val for p in ("http://", "https://", "t.me/", "@")):
            await _send_err()
            return

    await state.update_data(edit_parsed_value=parsed_value)

    confirm_key = _CONFIRM_KEYS.get(param_name, "va_model_edit_param_name")
    confirm_prompt = t(confirm_key, value=formatted_value)
    confirm_kb = kb_param_confirm_update(code, param_name, back_target=f"admin:form:param:{code}:{param_name}")
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=bot_msg_id,
            text=confirm_prompt,
            parse_mode="HTML",
            reply_markup=confirm_kb,
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin:form:param-approve:"))
async def approve_edit_param(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    code = parts[3]
    param_name = parts[4]

    data = await state.get_data()
    parsed_val = data.get("edit_parsed_value")
    is_default = data.get("edit_is_default", False)
    await state.clear()

    if parsed_val is None:
        await call.answer("Ошибка: значение не задано", show_alert=True)
        return

    update_payload: dict[str, Any] = {}
    if param_name == "channel":
        update_payload["public_channel_url"] = str(parsed_val)
    else:
        update_payload[param_name] = parsed_val

    try:
        admin_id = await _resolve_admin_id(call.from_user)
        await api_client.admin.update_form(code, update_payload, admin_id=admin_id)
        await call.answer("✅ Изменено")
        if is_default:
            call.data = f"admin:form:edit:{code}"
            await edit_model_params_menu(call)
        else:
            await show_model_card(call, state, code=code)
    except Exception as exc:
        await call.answer(f"❌ Ошибка обновления: {exc}", show_alert=True)


@router.callback_query(F.data.startswith("admin:form:param-del-ask:"))
async def ask_delete_param(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    code = parts[3]
    param_name = parts[4]

    del_key = _DELETE_CONFIRM_KEYS.get(param_name)
    if not del_key:
        await call.answer("Параметр нельзя удалить", show_alert=True)
        return

    text = t(del_key)
    kb = kb_param_confirm_delete(code, param_name, back_target=f"admin:form:param:{code}:{param_name}")
    await _render_text_menu(call, text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:param-del-approve:"))
async def approve_delete_param(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    code = parts[3]
    param_name = parts[4]

    update_payload: dict[str, Any] = {}
    if param_name == "orders":
        update_payload["orders"] = 0
    elif param_name == "channel":
        update_payload["public_channel_url"] = ""
    elif param_name == "caption":
        update_payload["caption"] = ""
    elif param_name == "rating":
        update_payload["rating"] = 0.0
    else:
        update_payload[param_name] = None

    try:
        admin_id = await _resolve_admin_id(call.from_user)
        await api_client.admin.update_form(code, update_payload, admin_id=admin_id)
        await call.answer(t("va_model_param_deleted_answer"))
        await state.clear()
        if param_name in _DEFAULT_PARAMS:
            call.data = f"admin:form:edit:{code}"
            await edit_model_params_menu(call)
        else:
            await show_model_card(call, state, code=code)
    except Exception as exc:
        await call.answer(f"❌ Ошибка удаления: {exc}", show_alert=True)


# ── Управление фотографиями ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:form:photos:"))
async def show_form_photos(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    code = parts[3]
    index = int(parts[4])

    admin_id = await _resolve_admin_id(call.from_user)
    form = await api_client.admin.get_form(code, admin_id=admin_id)
    photos = form.photos or []
    count = len(photos)

    if count == 0:
        await _render_text_menu(
            call,
            t("model_photos_empty", code=code),
            reply_markup=kb_form_photos(code, 0, 0),
        )
        await call.answer()
        return

    current_idx = max(0, min(index, count - 1))
    storage_key = photos[current_idx]
    photo_bytes = await _fetch_photo_bytes(storage_key)

    caption = t("va_photo_caption", current=current_idx + 1, total=count)
    kb = kb_form_photos(code, count, current_idx)

    if photo_bytes:
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer_photo(
            photo=BufferedInputFile(photo_bytes, filename=f"photo_{current_idx}.jpg"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await _render_text_menu(call, caption, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:photo:del:"))
async def delete_form_photo(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    code = parts[4]
    index = int(parts[5])

    try:
        admin_id = await _resolve_admin_id(call.from_user)
        await api_client.admin.delete_form_photo(code, index, admin_id=admin_id)
        await call.answer(t("model_photos_deleted"))
    except Exception as exc:
        await call.answer(f"Ошибка удаления: {exc}", show_alert=True)
        return

    call.data = f"admin:form:photos:{code}:0"
    await show_form_photos(call, state)


async def _flush_add_album(user_id: int, bot: Bot, state: FSMContext):
    await asyncio.sleep(0.8)
    buf = _album_buffers.pop(user_id, None)
    if not buf:
        return
    for mid in buf.get("msg_ids", []):
        try:
            await bot.delete_message(user_id, mid)
        except Exception:
            pass
    items = buf.get("items", [])[:20]
    data = await state.get_data()
    code = data.get("photo_add_code")
    await state.clear()
    if not code or not items:
        return

    files = []
    for idx, item in enumerate(items):
        try:
            file_io = io.BytesIO()
            await bot.download(item["fid"], destination=file_io)
            files.append(("files", (f"photo_{idx}.jpg", file_io.getvalue(), "image/jpeg")))
        except Exception:
            logger.exception("Failed to download add photo %s", item["fid"])

    if files:
        try:
            await api_client.admin.add_form_photos(code, files=files)
            await bot.send_message(user_id, t("model_photos_added"))
        except Exception as exc:
            await bot.send_message(user_id, f"❌ Ошибка добавления: {exc}")

    try:
        admin_id = await _resolve_admin_id_by_tg(user_id)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
        await bot.send_message(
            user_id,
            build_model_card_text(form),
            parse_mode="HTML",
            reply_markup=kb_model_card(form, form.city_slot),
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin:form:photo:add:"))
async def ask_add_photo(call: CallbackQuery, state: FSMContext) -> None:
    code = call.data.split(":")[4]
    await state.update_data(photo_add_code=code)
    await state.set_state(VAAddPhoto.waiting)
    await _render_text_menu(call, t("model_photos_add_prompt"), reply_markup=kb_back(f"admin:form:photos:{code}:0"))
    await call.answer()


@router.message(StateFilter(VAAddPhoto.waiting), F.photo)
async def process_add_photo(message: Message, state: FSMContext) -> None:
    fid = message.photo[-1].file_id
    await _buffer_media(message.from_user.id, fid, message, message.bot, state, _flush_add_album)


# ── Отзывы (Reviews) ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:form:reviews:"))
async def show_reviews(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[3]
    page = int(parts[4])

    reviews_resp = await api_client.admin.list_reviews(code)
    reviews = reviews_resp.items
    admin_id = await _resolve_admin_id(call.from_user)
    form = await api_client.admin.get_form(code, admin_id=admin_id)

    text = t("model_reviews_title", code=code, name=form.name, total=len(reviews))
    await _render_text_menu(call, text, reply_markup=kb_reviews_list(code, reviews, page=page))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:review:info:"))
async def show_review_card(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[4]
    review_id = int(parts[5])

    reviews_resp = await api_client.admin.list_reviews(code)
    review = next((r for r in reviews_resp.items if r.id == review_id), None)
    if not review:
        await call.answer("Отзыв не найден", show_alert=True)
        return

    text = t(
        "va_model_review_card",
        author=review.author,
        date=review.review_date,
        score=review.score,
        id=review.id,
        text=review.body,
        created_ad=review.review_date,
    )
    await _render_text_menu(call, text, reply_markup=kb_review_card(code, review_id))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:review:del:"))
async def delete_review(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[4]
    review_id = int(parts[5])

    await api_client.admin.delete_review(review_id)
    await call.answer(t("model_review_deleted"))
    call.data = f"admin:form:reviews:{code}:1"
    await show_reviews(call)


@router.callback_query(F.data.startswith("admin:form:review:add:"))
async def ask_add_review(call: CallbackQuery, state: FSMContext) -> None:
    code = call.data.split(":")[4]
    await state.update_data(
        review_target_code=code,
        review_bot_msg_id=call.message.message_id,
        review_bot_chat_id=call.message.chat.id,
    )
    await state.set_state(VANewReview.input_text)
    await _render_text_menu(call, t("model_review_add_prompt"), reply_markup=kb_back(f"admin:form:reviews:{code}:1"))
    await call.answer()


@router.message(StateFilter(VANewReview.input_text), F.chat.type == "private")
async def process_add_review(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    code = data.get("review_target_code")
    bot_msg_id = data.get("review_bot_msg_id")
    chat_id = data.get("review_bot_chat_id") or message.chat.id
    raw = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not code or not bot_msg_id:
        await state.clear()
        return

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=f"{t('model_review_invalid')}\n\n{t('model_review_add_prompt')}",
                parse_mode="HTML",
                reply_markup=kb_back(f"admin:form:reviews:{code}:1"),
            )
        except Exception:
            pass
        return

    parsed_reviews = []
    for line in lines:
        parts = [p.strip() for p in line.split(";")]
        if len(parts) != 4 or not parts[3].isdigit() or not (1 <= int(parts[3]) <= 5):
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=f"{t('model_review_invalid')}\n\n<b>Некорректная строка:</b> <code>{line}</code>\n\n{t('model_review_add_prompt')}",
                    parse_mode="HTML",
                    reply_markup=kb_back(f"admin:form:reviews:{code}:1"),
                )
            except Exception:
                pass
            return
        parsed_reviews.append({
            "author": parts[0],
            "review_date": parts[1],
            "body": parts[2],
            "score": int(parts[3]),
        })

    await state.clear()
    try:
        for rev in parsed_reviews:
            await api_client.admin.create_review(code, rev)
        reviews_resp = await api_client.admin.list_reviews(code)
        reviews = reviews_resp.items
        admin_id = await _resolve_admin_id(message.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
        text = t("model_reviews_title", code=code, name=form.name, total=len(reviews))
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=bot_msg_id,
            text=text,
            parse_mode="HTML",
            reply_markup=kb_reviews_list(code, reviews, page=1),
        )
    except Exception as exc:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=f"❌ Ошибка добавления отзыва: {exc}",
                parse_mode="HTML",
                reply_markup=kb_back(f"admin:form:reviews:{code}:1"),
            )
        except Exception:
            pass


# ── Услуги (Services) ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:form:services:"))
async def show_services(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[3]
    page = int(parts[4])

    services_resp = await api_client.admin.list_services(code)
    services = services_resp.items
    admin_id = await _resolve_admin_id(call.from_user)
    form = await api_client.admin.get_form(code, admin_id=admin_id)

    text = t("model_services_title", code=code, name=form.name, total=len(services))
    await _render_text_menu(call, text, reply_markup=kb_services_list(code, services, page=page))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:service:info:"))
async def show_service_card(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[4]
    service_id = int(parts[5])

    services_resp = await api_client.admin.list_services(code)
    service = next((s for s in services_resp.items if s.id == service_id), None)
    if not service:
        await call.answer("Услуга не найдена", show_alert=True)
        return

    from bot.keyboards.forms import kb_service_card
    text = t("va_model_service_card", name=service.name, id=service.id, created_at="—")
    await _render_text_menu(call, text, reply_markup=kb_service_card(code, service_id))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:service:del:"))
async def delete_service(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[4]
    service_id = int(parts[5])

    await api_client.admin.delete_service(service_id)
    await call.answer(t("model_service_deleted"))
    call.data = f"admin:form:services:{code}:1"
    await show_services(call)


@router.callback_query(F.data.startswith("admin:form:service:add:"))
async def ask_add_service(call: CallbackQuery, state: FSMContext) -> None:
    code = call.data.split(":")[4]
    await state.update_data(
        service_target_code=code,
        service_bot_msg_id=call.message.message_id,
        service_bot_chat_id=call.message.chat.id,
    )
    await state.set_state(VANewService.input_text)
    await _render_text_menu(call, t("model_service_add_prompt"), reply_markup=kb_back(f"admin:form:services:{code}:1"))
    await call.answer()


@router.message(StateFilter(VANewService.input_text), F.chat.type == "private")
async def process_add_service(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    code = data.get("service_target_code")
    bot_msg_id = data.get("service_bot_msg_id")
    chat_id = data.get("service_bot_chat_id") or message.chat.id
    raw = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not code or not raw or not bot_msg_id:
        await state.clear()
        return

    names = []
    for line in raw.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        for item in line_clean.replace(";", "\n").replace(",", "\n").splitlines():
            item_clean = item.strip()
            if item_clean:
                names.append(item_clean)

    if not names:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=f"❌ Введите корректное название услуги\n\n{t('model_service_add_prompt')}",
                parse_mode="HTML",
                reply_markup=kb_back(f"admin:form:services:{code}:1"),
            )
        except Exception:
            pass
        return

    await state.clear()
    try:
        for name in names:
            await api_client.admin.create_service(code, {"name": name})
        services_resp = await api_client.admin.list_services(code)
        services = services_resp.items
        admin_id = await _resolve_admin_id(message.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
        text = t("model_services_title", code=code, name=form.name, total=len(services))
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=bot_msg_id,
            text=text,
            parse_mode="HTML",
            reply_markup=kb_services_list(code, services, page=1),
        )
    except Exception as exc:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=f"❌ Ошибка добавления услуги: {exc}",
                parse_mode="HTML",
                reply_markup=kb_back(f"admin:form:services:{code}:1"),
            )
        except Exception:
            pass


# ── Дополнительные услуги (Additionals) ───────────────────────────────────────

@router.callback_query(F.data.startswith("admin:form:additionals:"))
async def show_additionals(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[3]
    page = int(parts[4])

    adds_resp = await api_client.admin.list_additionals(code)
    additionals = adds_resp.items
    admin_id = await _resolve_admin_id(call.from_user)
    form = await api_client.admin.get_form(code, admin_id=admin_id)

    text = t("model_additionals_title", code=code, name=form.name, total=len(additionals))
    await _render_text_menu(call, text, reply_markup=kb_additionals_list(code, additionals, page=page))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:additional:info:"))
async def show_additional_card(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[4]
    add_id = int(parts[5])

    adds_resp = await api_client.admin.list_additionals(code)
    add = next((a for a in adds_resp.items if a.id == add_id), None)
    if not add:
        await call.answer("Доп. услуга не найдена", show_alert=True)
        return

    from bot.keyboards.forms import kb_additional_card
    text = t("va_model_additional_card", name=add.name, price=f"{add.price} RUB", id=add.id, created_at="—")
    await _render_text_menu(call, text, reply_markup=kb_additional_card(code, add_id))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:additional:del:"))
async def delete_additional(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    code = parts[4]
    add_id = int(parts[5])

    await api_client.admin.delete_additional(add_id)
    await call.answer(t("model_additional_deleted"))
    call.data = f"admin:form:additionals:{code}:1"
    await show_additionals(call)


@router.callback_query(F.data.startswith("admin:form:additional:add:"))
async def ask_add_additional(call: CallbackQuery, state: FSMContext) -> None:
    code = call.data.split(":")[4]
    await state.update_data(
        add_target_code=code,
        add_bot_msg_id=call.message.message_id,
        add_bot_chat_id=call.message.chat.id,
    )
    await state.set_state(VANewAdditional.input_text)
    await _render_text_menu(call, t("model_additional_add_prompt"), reply_markup=kb_back(f"admin:form:additionals:{code}:1"))
    await call.answer()


@router.message(StateFilter(VANewAdditional.input_text), F.chat.type == "private")
async def process_add_additional(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    code = data.get("add_target_code")
    bot_msg_id = data.get("add_bot_msg_id")
    chat_id = data.get("add_bot_chat_id") or message.chat.id
    raw = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not code or not raw or not bot_msg_id:
        await state.clear()
        return

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=f"{t('model_additional_invalid')}\n\n{t('model_additional_add_prompt')}",
                parse_mode="HTML",
                reply_markup=kb_back(f"admin:form:additionals:{code}:1"),
            )
        except Exception:
            pass
        return

    parsed_additionals = []
    for line in lines:
        parts = [p.strip() for p in line.split(";")]
        if len(parts) != 2 or not parts[1].isdigit():
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=f"{t('model_additional_invalid')}\n\n<b>Некорректная строка:</b> <code>{line}</code>\n\n{t('model_additional_add_prompt')}",
                    parse_mode="HTML",
                    reply_markup=kb_back(f"admin:form:additionals:{code}:1"),
                )
            except Exception:
                pass
            return
        parsed_additionals.append({
            "name": parts[0],
            "price": int(parts[1]),
        })

    await state.clear()
    try:
        for add_item in parsed_additionals:
            await api_client.admin.create_additional(code, add_item)
        adds_resp = await api_client.admin.list_additionals(code)
        additionals = adds_resp.items
        admin_id = await _resolve_admin_id(message.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
        text = t("model_additionals_title", code=code, name=form.name, total=len(additionals))
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=bot_msg_id,
            text=text,
            parse_mode="HTML",
            reply_markup=kb_additionals_list(code, additionals, page=1),
        )
    except Exception as exc:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=f"❌ Ошибка добавления: {exc}",
                parse_mode="HTML",
                reply_markup=kb_back(f"admin:form:additionals:{code}:1"),
            )
        except Exception:
            pass


# ── Смена позиций (Positions) ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:forms:positions:"))
async def show_positions(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    city_slot = int(parts[3])
    page = int(parts[4])

    admin_id = await _resolve_admin_id(call.from_user)
    forms_resp = await api_client.admin.list_forms(city_slot=city_slot, admin_id=admin_id)
    forms = forms_resp.items

    await _render_text_menu(call, t("va_positions_header"), reply_markup=kb_positions(forms, city_slot, page=page))
    await call.answer()


@router.callback_query(F.data.startswith("admin:form:pos-up:"))
async def pos_up(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    city_slot = int(parts[3])
    code = parts[4]

    admin_id = await _resolve_admin_id(call.from_user)
    forms_resp = await api_client.admin.list_forms(city_slot=city_slot, admin_id=admin_id)
    forms = forms_resp.items
    codes = [f.code for f in forms]
    idx = codes.index(code) if code in codes else -1
    if idx > 0:
        await api_client.admin.swap_positions(codes[idx - 1], code, admin_id=admin_id)
        await call.answer("⬆️")
    else:
        await call.answer()

    call.data = f"admin:forms:positions:{city_slot}:1"
    await show_positions(call)


@router.callback_query(F.data.startswith("admin:form:pos-down:"))
async def pos_down(call: CallbackQuery) -> None:
    parts = call.data.split(":")
    city_slot = int(parts[3])
    code = parts[4]

    admin_id = await _resolve_admin_id(call.from_user)
    forms_resp = await api_client.admin.list_forms(city_slot=city_slot, admin_id=admin_id)
    forms = forms_resp.items
    codes = [f.code for f in forms]
    idx = codes.index(code) if code in codes else -1
    if 0 <= idx < len(codes) - 1:
        await api_client.admin.swap_positions(code, codes[idx + 1], admin_id=admin_id)
        await call.answer("⬇️")
    else:
        await call.answer()

    call.data = f"admin:forms:positions:{city_slot}:1"
    await show_positions(call)


# ── Удаление анкеты ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:form:del:confirm:"))
async def confirm_delete_model(call: CallbackQuery, state: FSMContext) -> None:
    code = call.data.split(":")[4]
    try:
        admin_id = await _resolve_admin_id(call.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
        city_slot = form.city_slot
        await api_client.admin.delete_form(code, admin_id=admin_id)
        await call.answer(t("model_deleted_answer"))
        call.data = f"admin:forms:city:{city_slot}:1"
        await show_forms_list(call, state)
    except Exception as exc:
        await call.answer(f"Ошибка удаления: {exc}", show_alert=True)


@router.callback_query(F.data.startswith("admin:form:del:"))
async def ask_delete_model(call: CallbackQuery) -> None:
    code = call.data.split(":")[3]
    try:
        admin_id = await _resolve_admin_id(call.from_user)
        form = await api_client.admin.get_form(code, admin_id=admin_id)
    except ApiNotFoundError:
        await call.answer("Анкета не найдена", show_alert=True)
        return

    text = t("model_delete_confirm", code=code, name=form.name)
    await _render_text_menu(call, text, reply_markup=kb_confirm_delete_model(code, form.city_slot))
    await call.answer()


@router.callback_query(F.data == "admin:noop")
async def noop(call: CallbackQuery) -> None:
    await call.answer()
