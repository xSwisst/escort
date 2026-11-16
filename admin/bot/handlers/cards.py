from __future__ import annotations

import re
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.texts import t
from bot.keyboards import (
    kb_approve_new_card,
    kb_back,
    kb_card_card,
    kb_cards_list,
    kb_confirm_delete_card,
)
from bot.states import VANewCard
from clients.api import api_client
from shared.utils.date import format_datetime_ru

router = Router(name="admin_cards")


def _format_card_detail_text(card) -> str:
    status_str = "🟢 Включена" if card.is_active else "🔴 Выключена"
    created_at_str = format_datetime_ru(card.created_at) if getattr(card, "created_at", None) else "—"
    min_str = f"{card.min_amount:,}".replace(",", " ")
    max_str = f"{card.max_amount:,}".replace(",", " ")
    created_by_str = card.created_by or "Администратор"

    return t(
        "va_card_info",
        card_number=card.card_number,
        min_amount=min_str,
        max_amount=max_str,
        status=status_str,
        created_by=created_by_str,
        created_at=created_at_str,
    )


@router.callback_query(F.data.startswith("admin:cards:list:"))
async def show_cards_list(call: CallbackQuery, state: FSMContext, page: int | None = None) -> None:
    await state.clear()
    if page is None:
        try:
            page = int(call.data.split(":")[3])
        except Exception:
            page = 1
    resp = await api_client.admin.list_cards()
    cards = resp.items
    await call.message.edit_text(
        t("va_cards_list_title"),
        parse_mode="HTML",
        reply_markup=kb_cards_list(cards, page=page),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:card:info:"))
async def show_card_detail(call: CallbackQuery) -> None:
    card_id = int(call.data.split(":")[3])
    resp = await api_client.admin.list_cards()
    card = next((c for c in resp.items if c.id == card_id), None)
    if not card:
        await call.answer(t("va_card_not_found"), show_alert=True)
        return

    text = _format_card_detail_text(card)
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb_card_card(card))
    await call.answer()


@router.callback_query(F.data.startswith("admin:card:toggle:"))
async def toggle_card_status(call: CallbackQuery) -> None:
    card_id = int(call.data.split(":")[3])
    try:
        updated_card = await api_client.admin.toggle_card(card_id)
        text = _format_card_detail_text(updated_card)
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb_card_card(updated_card))
        status_msg = "Карта включена" if updated_card.is_active else "Карта отключена"
        await call.answer(status_msg)
    except Exception as exc:
        await call.answer(f"Ошибка переключения: {exc}", show_alert=True)


@router.callback_query(F.data.startswith("admin:card:del:confirm:"))
async def confirm_delete_card(call: CallbackQuery, state: FSMContext) -> None:
    card_id = int(call.data.split(":")[4])
    try:
        await api_client.admin.delete_card(card_id)
        await call.answer(t("va_card_deleted_answer"))
    except Exception as exc:
        await call.answer(f"Ошибка удаления: {exc}", show_alert=True)
        return
    await show_cards_list(call, state, page=1)


@router.callback_query(F.data.startswith("admin:card:del:"))
async def ask_delete_card(call: CallbackQuery) -> None:
    card_id = int(call.data.split(":")[3])
    await call.message.edit_text(
        t("va_card_delete_confirm"),
        parse_mode="HTML",
        reply_markup=kb_confirm_delete_card(card_id),
    )
    await call.answer()


# ── FSM Создание карты ────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:card:new")
async def start_new_card(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(VANewCard.number)
    await state.update_data(
        card_bot_msg_id=call.message.message_id,
        card_bot_chat_id=call.message.chat.id,
    )
    await call.message.edit_text(
        t("va_card_new_step1_number"),
        parse_mode="HTML",
        reply_markup=kb_back("admin:cards:list:1"),
    )
    await call.answer()


@router.message(StateFilter(VANewCard.number), F.chat.type == "private")
async def process_card_number(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    bot_msg_id = data.get("card_bot_msg_id")
    chat_id = data.get("card_bot_chat_id") or message.chat.id

    raw = (message.text or "").strip()
    digits_only = "".join(c for c in raw if c.isdigit())

    if len(digits_only) < 12 or len(digits_only) > 19:
        error_text = t("va_card_invalid_number")
        if bot_msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=error_text,
                    parse_mode="HTML",
                    reply_markup=kb_back("admin:cards:list:1"),
                )
                return
            except Exception:
                pass
        sent = await message.answer(error_text, parse_mode="HTML", reply_markup=kb_back("admin:cards:list:1"))
        await state.update_data(card_bot_msg_id=sent.message_id)
        return

    # Форматируем номер карты с пробелами по 4 цифры
    formatted_number = " ".join(digits_only[i : i + 4] for i in range(0, len(digits_only), 4))
    await state.update_data(new_card_number=formatted_number)
    await state.set_state(VANewCard.limits)

    step2_text = t("va_card_new_step2_limits", card_number=formatted_number)
    if bot_msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=step2_text,
                parse_mode="HTML",
                reply_markup=kb_back("admin:cards:list:1"),
            )
            return
        except Exception:
            pass
    sent = await message.answer(step2_text, parse_mode="HTML", reply_markup=kb_back("admin:cards:list:1"))
    await state.update_data(card_bot_msg_id=sent.message_id)


@router.message(StateFilter(VANewCard.limits), F.chat.type == "private")
async def process_card_limits(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    bot_msg_id = data.get("card_bot_msg_id")
    chat_id = data.get("card_bot_chat_id") or message.chat.id
    card_number = data.get("new_card_number", "")

    raw = (message.text or "").strip()
    # Ищем числа (например "1000 50000", "1000-50000", "1000; 50000")
    numbers = [int(n) for n in re.findall(r"\d+", raw)]

    if len(numbers) == 1:
        min_amount = 0
        max_amount = numbers[0]
    elif len(numbers) >= 2:
        min_amount = min(numbers[0], numbers[1])
        max_amount = max(numbers[0], numbers[1])
    else:
        error_text = t("va_card_invalid_limits")
        if bot_msg_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bot_msg_id,
                    text=error_text,
                    parse_mode="HTML",
                    reply_markup=kb_back("admin:cards:list:1"),
                )
                return
            except Exception:
                pass
        sent = await message.answer(error_text, parse_mode="HTML", reply_markup=kb_back("admin:cards:list:1"))
        await state.update_data(card_bot_msg_id=sent.message_id)
        return

    await state.update_data(new_card_min=min_amount, new_card_max=max_amount)
    await state.set_state(VANewCard.confirm)

    min_str = f"{min_amount:,}".replace(",", " ")
    max_str = f"{max_amount:,}".replace(",", " ")
    confirm_text = t(
        "va_card_new_confirm",
        card_number=card_number,
        min_amount=min_str,
        max_amount=max_str,
    )

    if bot_msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=bot_msg_id,
                text=confirm_text,
                parse_mode="HTML",
                reply_markup=kb_approve_new_card(),
            )
            return
        except Exception:
            pass
    sent = await message.answer(confirm_text, parse_mode="HTML", reply_markup=kb_approve_new_card())
    await state.update_data(card_bot_msg_id=sent.message_id)


@router.callback_query(F.data == "admin:card:new:approve", StateFilter(VANewCard.confirm))
async def approve_new_card(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    card_number = data.get("new_card_number")
    min_amount = data.get("new_card_min", 0)
    max_amount = data.get("new_card_max", 1_000_000)

    if not card_number:
        await call.answer("Ошибка: номер карты не найден", show_alert=True)
        await state.clear()
        await show_cards_list(call, state, page=1)
        return

    creator = (
        f"@{call.from_user.username}"
        if call.from_user.username
        else (call.from_user.full_name or str(call.from_user.id))
    )

    try:
        await api_client.admin.create_card(
            {
                "card_number": card_number,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "created_by": creator,
            }
        )
        await call.answer(t("va_card_created_success"))
    except Exception as exc:
        await call.answer(f"❌ Ошибка создания: {exc}", show_alert=True)
        return

    await state.clear()
    await show_cards_list(call, state, page=1)
