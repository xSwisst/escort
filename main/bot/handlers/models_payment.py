from __future__ import annotations

import uuid

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.keyboards.models_catalog import kb_private_channel_view
from bot.keyboards.models_order import kb_card_payment, kb_card_payment_with_card, kb_check_prompt
from bot.states import OrderCheckState
from clients.api import ApiNotFoundError, api_client
from clients.logs import emit_log_event
from shared.bot.utils.media_banner import edit_banner

router = Router(name="models_payment")


@router.callback_query(F.data.startswith("pchan:method:"))
async def private_channel_method(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    if len(parts) != 4:
        await call.answer()
        return
    _, _, code, method_key = parts

    if method_key != "card":
        await call.answer(t("models_pay_method_disabled"), show_alert=True)
        return

    try:
        channel_info = await api_client.forms.get_private_channel(code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return

    order_number = uuid.uuid4().hex[:8].upper()
    price = int(channel_info.price or 0)

    await state.update_data(
        pchan_order_number=order_number,
        pchan_code=code,
        pchan_name=channel_info.name,
        pchan_price=price,
    )

    card = await api_client.cards.get_suitable_card(price)
    if card:
        text = t(
            "models_pay_card_card_text",
            order_number=order_number,
            model_name=channel_info.name,
            model_code=code,
            price=price,
            card_number=card.card_number,
        )
        markup = kb_card_payment_with_card(
            order_number,
            send_check_callback=f"pchan:send_check:{order_number}",
            back_callback=f"pchan:back:{code}",
        )
        requisites_snapshot = card.card_number
    else:
        text = t(
            "models_pay_card_text",
            order_number=order_number,
            model_name=channel_info.name,
            model_code=code,
            price=price,
        )
        markup = kb_card_payment(
            order_number,
            back_callback=f"pchan:back:{code}",
        )
        requisites_snapshot = None

    await edit_banner(
        call.message,
        text,
        banner=get_banner_file("payment-method-banner"),
        reply_markup=markup,
    )
    await call.answer()
    # Создаем запись в таблице PaymentInvoice
    try:
        await api_client.invoices.create_invoice(
            invoice_number=order_number,
            user_id=call.from_user.id,
            amount=int(price),
            purpose="private_channel",
            payment_method="Банковская карта",
            order_number=order_number,
            form_code=code,
            requisites_snapshot=requisites_snapshot,
        )
    except Exception:
        pass

    await emit_log_event(
        "payment_request",
        call.from_user.id,
        {
            "user_id": call.from_user.id,
            "first_name": call.from_user.first_name or "",
            "last_name": call.from_user.last_name or "",
            "username": call.from_user.username,
            "order_number": order_number,
            "model_info": f"{channel_info.name} ({code})",
            "tariff_plan": "Приватный канал",
            "additional": "Нет",
            "meet_info": "Приватный канал",
            "payment_method": "Банковская карта",
            "amount": str(price),
        },
    )


@router.callback_query(F.data.startswith("pchan:back:"))
async def private_channel_back(call: CallbackQuery):
    code = call.data.split(":")[2]
    try:
        channel_info = await api_client.forms.get_private_channel(code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return

    caption = t(
        "models_private_channel_caption",
        name=channel_info.name,
        code=code,
        description=channel_info.description or t("models_private_channel_default_description"),
        price=channel_info.price,
    )
    await edit_banner(
        call.message,
        caption,
        banner=get_banner_file("payment-method-banner"),
        reply_markup=kb_private_channel_view(code, payment_available=True),
    )
    await call.answer()


@router.callback_query(F.data.startswith("pchan:send_check:"))
async def private_channel_send_check(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[2]
    data = await state.get_data()
    code = data.get("pchan_code", "")

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
        reply_markup=kb_check_prompt(order_number, back_callback=f"pchan:method:{code}:card"),
    )
    await call.answer()
