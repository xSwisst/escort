from __future__ import annotations

import calendar
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.keyboards.common import kb_back
from bot.keyboards.models_order import (
    kb_addons,
    kb_balance_confirm,
    kb_card_payment,
    kb_card_payment_with_card,
    kb_check_prompt,
    kb_dates,
    kb_meeting_place,
    kb_months,
    kb_order_address_create_confirm,
    kb_order_address_select,
    kb_order_confirmed,
    kb_payment_method,
    kb_tariff,
    kb_times,
    tariff_label,
)
from bot.states import OrderAddressCreate, OrderCheckState
from clients.api import ApiNotFoundError, api_client
from clients.logs import emit_log_event
from shared.bot.utils.media_banner import bot_edit_banner, edit_banner

router = Router(name="models_order")

MSK_TZ = timezone(timedelta(hours=3))


def _now_msk() -> datetime:
    return datetime.now(MSK_TZ)


def _tariff_keyboard_flags(form) -> dict[str, bool]:
    return {
        "has_one_hour": bool(getattr(form, "one_hour_price", None)),
        "has_two_hours": bool(getattr(form, "two_hour_price", None)),
        "has_three_hours": bool(getattr(form, "three_hour_price", None)),
        "has_night": bool(getattr(form, "overnight_price", None)),
    }


def _get_available_tariffs(form) -> dict[str, int]:
    result: dict[str, int] = {}
    if getattr(form, "one_hour_price", None):
        result["1h"] = int(form.one_hour_price)
    if getattr(form, "two_hour_price", None):
        result["2h"] = int(form.two_hour_price)
    if getattr(form, "three_hour_price", None):
        result["3h"] = int(form.three_hour_price)
    if getattr(form, "overnight_price", None):
        result["night"] = int(form.overnight_price)
    return result


async def _open_tariff_step(
    call: CallbackQuery,
    state: FSMContext,
    *,
    code: str,
) -> bool:
    try:
        form = await api_client.forms.get_form_card(user_id=call.from_user.id, form_code=code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return False

    flags = _tariff_keyboard_flags(form)
    if not any(flags.values()):
        await call.answer("Тарифы недоступны", show_alert=True)
        return False

    await state.update_data(
        order_code=code,
        order_form_name=form.name,
        order_tariffs=_get_available_tariffs(form),
        order_discount=int(getattr(form, "discount_amount", 0) or 0),
    )

    await edit_banner(
        call.message,
        t("models_tariff_prompt", name=form.name),
        banner=get_banner_file("choice-tariff-plan-banner"),
        reply_markup=kb_tariff(code, **flags),
    )
    return True


# ─── 1. Start order: Month selection ──────────────────────────────────────────

@router.callback_query(F.data.startswith("model:order:"))
async def start_order(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":")[2]
    try:
        form = await api_client.forms.get_form_card(user_id=call.from_user.id, form_code=code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return

    tariffs = _get_available_tariffs(form)
    if not tariffs:
        await call.answer("Тарифы недоступны", show_alert=True)
        return

    await state.update_data(
        order_code=code,
        order_form_name=form.name,
        order_tariffs=tariffs,
        order_discount=int(getattr(form, "discount_amount", 0) or 0),
    )

    now = _now_msk()
    months = [(now.year, now.month)]
    nxt = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
    months.append((nxt.year, nxt.month))

    await edit_banner(
        call.message,
        t("models_choose_month"),
        banner=get_banner_file("date-meeting-banner"),
        reply_markup=kb_months(code, months),
    )
    await call.answer()


# ─── 2. Month → Date selection ────────────────────────────────────────────────

@router.callback_query(F.data.regexp(r"^order:month:"))
async def choose_month(call: CallbackQuery):
    parts = call.data.split(":")
    code, year, month = parts[2], int(parts[3]), int(parts[4])

    now = _now_msk()
    _, last_day = calendar.monthrange(year, month)

    if year == now.year and month == now.month:
        start_day = now.day
    else:
        start_day = 1

    dates = list(range(start_day, last_day + 1))

    await edit_banner(
        call.message,
        t("models_choose_date"),
        banner=get_banner_file("date-meeting-banner"),
        reply_markup=kb_dates(code, dates, year, month),
    )
    await call.answer()


# ─── 3. Date → Time selection ─────────────────────────────────────────────────

@router.callback_query(F.data.regexp(r"^order:date:"))
async def choose_date(call: CallbackQuery):
    parts = call.data.split(":")
    code = parts[2]
    year, month, day = int(parts[3]), int(parts[4]), int(parts[5])

    times = [f"{h:02d}:00" for h in range(1, 24)] + ["00:00"]
    date_key = f"{year}:{month}:{day}"

    await edit_banner(
        call.message,
        t("models_choose_time"),
        banner=get_banner_file("date-meeting-banner"),
        reply_markup=kb_times(code, times, date_key),
    )
    await call.answer()


# ─── 4. Time → Meeting place selection ────────────────────────────────────────

@router.callback_query(F.data.regexp(r"^order:time:"))
async def choose_time(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = parts[2]
    date_key = f"{parts[3]}:{parts[4]}:{parts[5]}"
    time_val = parts[6]

    await state.update_data(order_date_key=date_key, order_time=time_val)

    await edit_banner(
        call.message,
        t("models_choose_place"),
        banner=get_banner_file("place-meeting-banner"),
        reply_markup=kb_meeting_place(code, date_key, time_val),
    )
    await call.answer()


# ─── 5. Meeting place chosen ──────────────────────────────────────────────────

@router.callback_query(F.data.regexp(r"^order:place:[^:]+:\d+:\d+:\d+:[^:]+:(model|client)$"))
async def choose_place(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = parts[2]
    date_key = f"{parts[3]}:{parts[4]}:{parts[5]}"
    time_val = parts[6]
    place = parts[7]

    await state.update_data(
        order_code=code,
        order_date_key=date_key,
        order_time=time_val,
        order_place=place,
        order_address_id=None,
    )

    if place == "client":
        addresses = (await api_client.addresses.list(call.from_user.id)).items
        caption = t("models_choose_address") if addresses else t("models_no_addresses")
        await edit_banner(
            call.message,
            caption,
            banner=get_banner_file("address-banner"),
            reply_markup=kb_order_address_select(addresses),
        )
        await call.answer()
        return

    await _open_tariff_step(call, state, code=code)
    await call.answer()


@router.callback_query(F.data.regexp(r"^order:place-direct:[^:]+:(model|client)$"))
async def choose_place_direct(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = parts[2]
    place = parts[3]

    await state.update_data(
        order_code=code,
        order_place=place,
        order_address_id=None,
    )

    if place == "client":
        addresses = (await api_client.addresses.list(call.from_user.id)).items
        caption = t("models_choose_address") if addresses else t("models_no_addresses")
        await edit_banner(
            call.message,
            caption,
            banner=get_banner_file("address-banner"),
            reply_markup=kb_order_address_select(addresses),
        )
        await call.answer()
        return

    await _open_tariff_step(call, state, code=code)
    await call.answer()


# ─── 6. Address selection during order ────────────────────────────────────────

@router.callback_query(F.data.regexp(r"^oaddr:sel:\d+$"))
async def order_addr_select(call: CallbackQuery, state: FSMContext):
    addr_id = int(call.data.split(":")[2])
    await state.update_data(order_address_id=addr_id)

    data = await state.get_data()
    code = data.get("order_code", "")

    await _open_tariff_step(call, state, code=code)
    await call.answer()


@router.callback_query(F.data.regexp(r"^oaddr_page:\d+$"))
async def order_addr_page(call: CallbackQuery):
    page = int(call.data.split(":")[1]) - 1
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    await call.message.edit_reply_markup(reply_markup=kb_order_address_select(addresses, page=page))
    await call.answer()


@router.callback_query(F.data == "oaddr:add")
async def order_addr_add_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderAddressCreate.title)
    await state.update_data(oaddr_bot_msg_id=call.message.message_id)
    await edit_banner(
        call.message,
        t("address_create_title"),
        banner=get_banner_file("address-banner"),
        reply_markup=kb_back("back_to_addresses", "oaddr:cancel_add"),
    )
    await call.answer()


@router.callback_query(F.data == "oaddr:cancel_add")
async def order_addr_cancel_add(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    caption = t("models_choose_address") if addresses else t("models_no_addresses")
    await edit_banner(
        call.message,
        caption,
        banner=get_banner_file("address-banner"),
        reply_markup=kb_order_address_select(addresses),
    )
    await call.answer()


@router.message(OrderAddressCreate.title)
async def order_addr_add_title(msg: Message, state: FSMContext):
    await msg.delete()
    title = msg.text.strip()[:256]
    await state.update_data(oaddr_title=title)
    await state.set_state(OrderAddressCreate.address)
    data = await state.get_data()
    await bot_edit_banner(
        msg.bot,
        msg.chat.id,
        data["oaddr_bot_msg_id"],
        t("address_create_address"),
        banner=get_banner_file("address-banner"),
        reply_markup=kb_back("back_to_addresses", "oaddr:cancel_add"),
    )


@router.message(OrderAddressCreate.address)
async def order_addr_add_address(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    title = data.get("oaddr_title", "")
    address_text = msg.text.strip()[:1000]
    await state.update_data(oaddr_address=address_text)
    await state.set_state(None)

    await bot_edit_banner(
        msg.bot,
        msg.chat.id,
        data["oaddr_bot_msg_id"],
        t("address_create_confirm", title=title, address=address_text),
        banner=get_banner_file("address-banner"),
        reply_markup=kb_order_address_create_confirm(),
    )


@router.callback_query(F.data == "oaddr:add_yes")
async def order_addr_add_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title = data.get("oaddr_title", "")
    address_text = data.get("oaddr_address", "")
    await state.set_state(None)

    if title and address_text:
        await api_client.addresses.create(user_id=call.from_user.id, title=title, address=address_text)

    addresses = (await api_client.addresses.list(call.from_user.id)).items
    caption = t("models_choose_address") if addresses else t("models_no_addresses")
    await edit_banner(
        call.message,
        caption,
        banner=get_banner_file("address-banner"),
        reply_markup=kb_order_address_select(addresses),
    )
    await call.answer(t("address_created"))


@router.callback_query(F.data == "oaddr:add_cancel")
async def order_addr_add_cancel_cb(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    caption = t("models_choose_address") if addresses else t("models_no_addresses")
    await edit_banner(
        call.message,
        caption,
        banner=get_banner_file("address-banner"),
        reply_markup=kb_order_address_select(addresses),
    )
    await call.answer()


@router.callback_query(F.data == "oaddr:back")
async def order_addr_back(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code = data.get("order_code", "")
    date_key = data.get("order_date_key", "")
    time_val = data.get("order_time", "")

    await edit_banner(
        call.message,
        t("models_choose_place"),
        banner=get_banner_file("place-meeting-banner"),
        reply_markup=kb_meeting_place(code, date_key or None, time_val or None),
    )
    await call.answer()


# ─── 7. Back from tariff ──────────────────────────────────────────────────────

@router.callback_query(F.data == "order:back_to_place")
async def back_to_place(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code = data.get("order_code", "")
    date_key = data.get("order_date_key", "")
    time_val = data.get("order_time", "")
    place = data.get("order_place", "")

    if place == "client":
        addresses = (await api_client.addresses.list(call.from_user.id)).items
        caption = t("models_choose_address") if addresses else t("models_no_addresses")
        await edit_banner(
            call.message,
            caption,
            banner=get_banner_file("address-banner"),
            reply_markup=kb_order_address_select(addresses),
        )
    else:
        await edit_banner(
            call.message,
            t("models_choose_place"),
            banner=get_banner_file("place-meeting-banner"),
            reply_markup=kb_meeting_place(code, date_key or None, time_val or None),
        )
    await call.answer()


# ─── 8. Tariff chosen → Addons / Payment method ───────────────────────────────

@router.callback_query(F.data.startswith("tariff:"))
async def choose_tariff(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code, tariff = parts[1], parts[2]

    data = await state.get_data()
    tariffs = data.get("order_tariffs") or {}
    form_name = data.get("order_form_name") or code

    if not tariffs or tariff not in tariffs:
        try:
            form = await api_client.forms.get_form_card(user_id=call.from_user.id, form_code=code)
            tariffs = _get_available_tariffs(form)
            form_name = form.name
            discount = int(getattr(form, "discount_amount", 0) or 0)
        except ApiNotFoundError:
            await call.answer(t("model_not_found"), show_alert=True)
            return
    else:
        discount = int(data.get("order_discount", 0) or 0)

    if tariff not in tariffs:
        await call.answer("Тариф недоступен", show_alert=True)
        return

    base_price = tariffs[tariff]
    final_price = max(base_price - discount, 0)
    try:
        created_order = await api_client.orders.create_order({
            "user_id": call.from_user.id,
            "form_code": code,
            "form_snapshot": form_name,
            "tariff_name": tariff_label(tariff),
            "city_name": data.get("order_city_name"),
            "promo_code": data.get("order_promo_code"),
            "scheduled_month": data.get("order_month"),
            "scheduled_day": data.get("order_date_key"),
            "scheduled_time": data.get("order_time"),
            "meeting_place_type": data.get("order_place_type"),
            "address_id": data.get("order_address_id"),
        })
        order_number = str(created_order.id)
    except Exception:
        order_number = "18245"

    await state.update_data(
        order_number=order_number,
        order_id=int(order_number) if order_number.isdigit() else None,
        order_code=code,
        order_form_name=form_name,
        order_tariff=tariff,
        order_base_price=final_price,
        order_total_sum=final_price,
    )

    # Check for addons
    try:
        addons_response = await api_client.forms.get_additionals(code)
        addons = [(item.name, item.price) for item in addons_response.items]
    except Exception:
        addons = []

    if addons:
        await state.update_data(**{
            f"addon_sel_{order_number}": [],
            f"addons_list_{order_number}": addons,
        })
        await edit_banner(
            call.message,
            t("models_addons_prompt"),
            banner=get_banner_file("additional-banner"),
            reply_markup=kb_addons(addons, set(), order_number, code),
        )
    else:
        await edit_banner(
            call.message,
            t("models_order_caption", order_number=order_number, model=form_name, tariff=tariff_label(tariff), price=final_price),
            banner=get_banner_file("payment-method-banner"),
            reply_markup=kb_payment_method(order_number),
        )
    await call.answer()


# ─── 9. Addons toggle & next & back ───────────────────────────────────────────

@router.callback_query(F.data.startswith("addon:toggle:"))
async def addon_toggle(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    order_number = parts[2]
    idx = int(parts[3])

    data = await state.get_data()
    code = data.get("order_code", "")
    addons = data.get(f"addons_list_{order_number}", [])
    sel = set(data.get(f"addon_sel_{order_number}", []))

    if idx in sel:
        sel.discard(idx)
    else:
        sel.add(idx)

    await state.update_data(**{f"addon_sel_{order_number}": list(sel)})

    await edit_banner(
        call.message,
        t("models_addons_prompt"),
        banner=get_banner_file("additional-banner"),
        reply_markup=kb_addons(addons, sel, order_number, code),
    )
    await call.answer()


@router.callback_query(F.data.startswith("addon:next:"))
async def addon_next(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[2]
    data = await state.get_data()

    code = data.get("order_code", "")
    form_name = data.get("order_form_name", code)
    tariff = data.get("order_tariff", "1h")
    base_price = data.get("order_base_price", 0)
    addons = data.get(f"addons_list_{order_number}", [])
    sel = set(data.get(f"addon_sel_{order_number}", []))

    selected_addons = [addons[i] for i in sel if i < len(addons)]
    extra_sum = sum(p for _, p in selected_addons)
    total_sum = base_price + extra_sum

    await state.update_data(order_total_sum=total_sum)

    await edit_banner(
        call.message,
        t("models_order_caption", order_number=order_number, model=form_name, tariff=tariff_label(tariff), price=total_sum),
        banner=get_banner_file("payment-method-banner"),
        reply_markup=kb_payment_method(order_number),
    )
    await call.answer()


@router.callback_query(F.data.startswith("addon:back:"))
async def addon_back(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code = data.get("order_code", "")
    await _open_tariff_step(call, state, code=code)
    await call.answer()


@router.callback_query(F.data.startswith("pay_back_addons:"))
async def pay_back_addons(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[1]
    data = await state.get_data()
    code = data.get("order_code", "")
    addons = data.get(f"addons_list_{order_number}", [])
    sel = set(data.get(f"addon_sel_{order_number}", []))

    if addons:
        await edit_banner(
            call.message,
            t("models_addons_prompt"),
            banner=get_banner_file("additional-banner"),
            reply_markup=kb_addons(addons, sel, order_number, code),
        )
    else:
        await _open_tariff_step(call, state, code=code)
    await call.answer()


@router.callback_query(F.data.startswith("pay:back:"))
async def pay_back(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[2]
    data = await state.get_data()
    code = data.get("order_code", "")
    form_name = data.get("order_form_name", code)
    tariff = data.get("order_tariff", "1h")
    total_sum = data.get("order_total_sum", 0)

    await state.set_state(None)
    await edit_banner(
        call.message,
        t("models_order_caption", order_number=order_number, model=form_name, tariff=tariff_label(tariff), price=total_sum),
        banner=get_banner_file("payment-method-banner"),
        reply_markup=kb_payment_method(order_number),
    )
    await call.answer()


# ─── 10. Payment methods ──────────────────────────────────────────────────────

async def _emit_new_order_log(user_id: int, user: Any, data: dict, order_number: str, total_sum: int) -> None:
    code = data.get("order_code", "")
    form_name = data.get("order_form_name", code)
    tariff = data.get("order_tariff", "1h")
    addons = data.get(f"addons_list_{order_number}", [])
    sel = set(data.get(f"addon_sel_{order_number}", []))
    selected_addons = [addons[i][0] for i in sel if i < len(addons)]
    additionals_str = ", ".join(selected_addons) if selected_addons else "Нет"
    place_type = data.get("order_place_type", "model")
    date_key = data.get("order_date_key", "")
    time_val = data.get("order_time", "")
    meeting_time = f"{date_key} {time_val}".strip() or "Не указано"

    await emit_log_event(
        "new_order",
        user_id,
        {
            "user_id": user_id,
            "first_name": getattr(user, "first_name", "") or "",
            "last_name": getattr(user, "last_name", "") or "",
            "username": getattr(user, "username", None),
            "order_id": order_number,
            "code": code,
            "model_name": form_name,
            "tariff_plan": tariff_label(tariff),
            "additionals": additionals_str,
            "place": "У модели" if place_type == "model" else "У клиента",
            "meeting_time": meeting_time,
            "amount": str(total_sum),
        },
    )


async def _emit_payment_request_log(
    user_id: int,
    user: Any,
    data: dict,
    order_number: str,
    payment_method: str = "Банковская карта",
    requisites_snapshot: str | None = None,
) -> None:
    code = data.get("order_code", "")
    form_name = data.get("order_form_name", code)
    total_sum = data.get("order_total_sum", 0)
    tariff = data.get("order_tariff", "1h")
    addons = data.get(f"addons_list_{order_number}", [])
    sel = set(data.get(f"addon_sel_{order_number}", []))
    selected_addons = [addons[i][0] for i in sel if i < len(addons)]
    additionals_str = ", ".join(selected_addons) if selected_addons else "Нет"
    place_type = data.get("order_place_type", "model")
    date_key = data.get("order_date_key", "")
    time_val = data.get("order_time", "")
    meeting_info = f"{'У модели' if place_type == 'model' else 'У клиента'} ({date_key} {time_val})".strip()

    # Создаем запись в таблице PaymentInvoice
    try:
        await api_client.invoices.create_invoice(
            invoice_number=order_number,
            user_id=user_id,
            amount=int(total_sum),
            purpose="order",
            payment_method=payment_method,
            order_number=order_number,
            form_code=code,
            requisites_snapshot=requisites_snapshot,
        )
    except Exception:
        pass

    await emit_log_event(
        "payment_request",
        user_id,
        {
            "user_id": user_id,
            "first_name": getattr(user, "first_name", "") or "",
            "last_name": getattr(user, "last_name", "") or "",
            "username": getattr(user, "username", None),
            "order_number": order_number,
            "model_info": f"{form_name} ({code})" if form_name else code,
            "tariff_plan": tariff_label(tariff),
            "additional": additionals_str,
            "meet_info": meeting_info,
            "payment_method": payment_method,
            "amount": str(total_sum),
        },
    )


async def _render_card_payment(call: CallbackQuery, state: FSMContext, order_number: str) -> None:
    data = await state.get_data()
    code = data.get("order_code", "")
    form_name = data.get("order_form_name", code)
    total_sum = int(data.get("order_total_sum", 0) or 0)

    card = await api_client.cards.get_suitable_card(total_sum)
    if card:
        text = t(
            "models_pay_card_card_text",
            order_number=order_number,
            model_name=form_name,
            model_code=code,
            price=total_sum,
            card_number=card.card_number,
        )
        markup = kb_card_payment_with_card(order_number)
        requisites_snapshot = card.card_number
    else:
        text = t(
            "models_pay_card_text",
            order_number=order_number,
            model_name=form_name,
            model_code=code,
            price=total_sum,
        )
        markup = kb_card_payment(order_number)
        requisites_snapshot = None

    await edit_banner(
        call.message,
        text,
        banner=get_banner_file("payment-method-banner"),
        reply_markup=markup,
    )
    await call.answer()
    await _emit_payment_request_log(
        call.from_user.id,
        call.from_user,
        data,
        order_number,
        "Банковская карта",
        requisites_snapshot=requisites_snapshot,
    )


@router.callback_query(F.data.startswith("pay:method:"))
async def pay_method(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    if len(parts) != 4:
        await call.answer()
        return
    _, _, order_number, method_key = parts

    if method_key == "card":
        await _render_card_payment(call, state, order_number)
        return

    if method_key == "balance":
        data = await state.get_data()
        total_sum = int(data.get("order_total_sum", 0) or 0)
        client = await api_client.profile.get_profile(call.from_user.id)
        user_balance = int(getattr(client, "balance", 0) or 0)
        if user_balance < total_sum:
            await call.answer(t("models_pay_balance_insufficient"))
            return

        text = t(
            "models_pay_balance_confirm",
            order_number=order_number,
            price=total_sum,
            balance=user_balance,
            balance_after=user_balance - total_sum,
        )
        await edit_banner(
            call.message,
            text,
            banner=get_banner_file("payment-method-banner"),
            reply_markup=kb_balance_confirm(order_number),
        )
        await call.answer()
        return

    if method_key == "cash":
        await call.answer(t("models_pay_cash_answer"), show_alert=True)
        return

    await call.answer(t("models_pay_method_disabled"), show_alert=True)


@router.callback_query(F.data.startswith("pay:confirm_balance:"))
async def pay_confirm_balance(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[2]
    data = await state.get_data()
    total_sum = int(data.get("order_total_sum", 0) or 0)
    code = data.get("order_code", "")
    form_name = data.get("order_form_name", code)
    tariff = data.get("order_tariff", "1h")

    client = await api_client.profile.get_profile(call.from_user.id)
    user_balance = int(getattr(client, "balance", 0) or 0)
    if user_balance < total_sum:
        await call.answer(t("models_pay_balance_insufficient"))
        return

    try:
        await api_client.orders.pay_balance(
            order_id=order_number,
            user_id=call.from_user.id,
            amount=total_sum,
        )
    except Exception as exc:
        logger.error("Failed to pay order %s with balance: %s", order_number, exc)
        await call.answer("Ошибка при списании средств. Обратитесь в поддержку.", show_alert=True)
        return

    await state.clear()

    text = t(
        "models_check_confirmed",
        order_number=order_number,
        model_name=form_name,
        tariff=tariff_label(tariff),
        price=f"{total_sum:,}".replace(",", " "),
    )
    await edit_banner(
        call.message,
        text,
        banner=get_banner_file("payment-success-banner"),
        reply_markup=kb_order_confirmed(),
    )
    await call.answer()

    await _emit_new_order_log(call.from_user.id, call.from_user, data, order_number, total_sum)


@router.callback_query(F.data.startswith("pay:card:"))
async def pay_card_cb(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[2]
    await state.set_state(None)
    await _render_card_payment(call, state, order_number)


# ─── 11. Send check flow ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("pay:send_check:"))
async def pay_send_check(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[2]
    await state.set_state(OrderCheckState.waiting_for_check)
    await state.update_data(
        check_order_number=order_number,
        check_bot_msg_id=call.message.message_id,
        check_chat_id=call.message.chat.id,
    )
    await edit_banner(
        call.message,
        t("models_check_prompt"),
        banner=get_banner_file("send-check-banner"),
        reply_markup=kb_check_prompt(order_number),
    )
    await call.answer()


@router.message(OrderCheckState.waiting_for_check, F.photo | F.document)
async def check_received(msg: Message, state: FSMContext):
    import base64
    import io
    data = await state.get_data()
    await state.set_state(None)
    order_number = data.get("check_order_number") or data.get("order_number") or ""
    code = data.get("order_code") or data.get("pchan_code") or ""
    form_name = data.get("order_form_name") or data.get("pchan_name") or code
    tariff = data.get("order_tariff", "1h")
    total_sum = (
        data.get("order_total_sum")
        or data.get("top_up_amount")
        or data.get("check_amount")
        or data.get("pchan_price")
        or 0
    )
    if not total_sum and order_number:
        try:
            inv = await api_client.invoices.get_invoice(order_number)
            if inv and getattr(inv, "amount", None):
                total_sum = inv.amount
        except Exception:
            pass
    bot_msg_id = data.get("check_bot_msg_id")

    try:
        await msg.delete()
    except Exception:
        pass

    if bot_msg_id:
        await bot_edit_banner(
            msg.bot,
            msg.chat.id,
            bot_msg_id,
            t("models_check_sent"),
            banner=get_banner_file("check-sent-banner"),
            reply_markup=kb_back("back_to_main", "menu:main"),
        )
    else:
        await msg.answer(t("models_check_sent"))

    photo_b64 = None
    if msg.photo:
        try:
            photo_io = io.BytesIO()
            await msg.bot.download(msg.photo[-1], destination=photo_io)
            photo_b64 = base64.b64encode(photo_io.getvalue()).decode("ascii")
        except Exception:
            pass

    # Check if this check is for deposit, private channel or model order
    if data.get("check_purpose") == "deposit":
        await emit_log_event(
            "get_check_of_top_up",
            msg.from_user.id,
            {
                "user_id": msg.from_user.id,
                "first_name": msg.from_user.first_name or "",
                "last_name": msg.from_user.last_name or "",
                "username": msg.from_user.username,
                "order_number": order_number,
                "invoice_number": order_number,
                "payment_method": "Банковская карта",
                "amount": str(total_sum),
                "photo_b64": photo_b64,
            },
        )
    elif data.get("pchan_code"):
        await emit_log_event(
            "get_check_of_payment_private_channel",
            msg.from_user.id,
            {
                "user_id": msg.from_user.id,
                "first_name": msg.from_user.first_name or "",
                "last_name": msg.from_user.last_name or "",
                "username": msg.from_user.username,
                "order_number": order_number,
                "invoice_number": order_number,
                "model_info": f"{form_name} ({code})" if form_name else code,
                "payment_method": "Банковская карта",
                "amount": str(total_sum),
                "photo_b64": photo_b64,
            },
        )
    else:
        await emit_log_event(
            "get_check_of_payment_model",
            msg.from_user.id,
            {
                "user_id": msg.from_user.id,
                "first_name": msg.from_user.first_name or "",
                "last_name": msg.from_user.last_name or "",
                "username": msg.from_user.username,
                "order_number": order_number,
                "invoice_number": order_number,
                "model_info": f"{form_name} ({code})" if form_name else code,
                "tariff_plan": tariff_label(tariff),
                "payment_method": "Банковская карта",
                "amount": str(total_sum),
                "photo_b64": photo_b64,
            },
        )
