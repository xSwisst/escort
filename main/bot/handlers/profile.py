import logging
import uuid

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.handlers.models_shared import get_form_card_payload
from bot.keyboards.common import kb_back
from bot.keyboards.models_order import kb_card_payment, kb_card_payment_with_card, kb_check_prompt
from bot.keyboards.profile import (
    kb_city_management,
    kb_orders_type,
    kb_profile,
    kb_profile_detail_back,
    kb_top_up_methods,
)
from bot.states import CityState, OrderCheckState, PromoState, TopUpState
from clients.api import api_client
from clients.logs import emit_log_event
from core.settings import settings
from shared.bot.utils.media_banner import answer_banner, bot_edit_banner, bot_edit_photo, edit_banner
from shared.utils.date import format_datetime_ru
from utils.helpers import models_banner_media

logger = logging.getLogger(__name__)

router = Router(name="profile")


_PAGE_SIZE = 10
MIN_TOP_UP_AMOUNT = 500
MAX_TOP_UP_AMOUNT = 300_000
MY_TRANSACTIONS_SEARCH_ICON = "https://img.icons8.com/color/96/banknodes.png"
MY_ORDERS_SEARCH_ICON = "https://img.icons8.com/color/96/shopping-bag.png"
MY_FAVORITES_SEARCH_ICON = "https://img.icons8.com/color/96/like--v3.png"


def _resolve_photo_thumbnail(photo_ref: str | None) -> str:
    if not photo_ref:
        return MY_FAVORITES_SEARCH_ICON
    cleaned = str(photo_ref).strip()
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    if settings.API_BASE_URL and cleaned.startswith("/"):
        return f"{settings.API_BASE_URL.rstrip('/')}{cleaned}"
    return MY_FAVORITES_SEARCH_ICON


def _get_active_city(client) -> str:
    active_city_slot = int(getattr(client, "active_city_slot", 1) or 1)
    active_city = client.primary_city if active_city_slot == 1 else client.secondary_city
    return active_city or client.primary_city or client.secondary_city or t("profile_city_not_set")


@router.callback_query(F.data == "menu:profile")
async def show_profile(call: CallbackQuery, state: FSMContext | None = None):
    if state:
        await state.clear()
        await state.update_data(bot_msg_id=call.message.message_id)
    client = await api_client.profile.get_profile(call.from_user.id)
    text = t(
        "profile_caption",
        id=client.id if client.id is not None else client.user_id,
        city=_get_active_city(client),
        balance=f"{getattr(client, 'balance', 0)} ₽",
        rating=client.rating,
        orders=client.orders,
        promo_status=t("profile_promo_active") if client.promo else t("profile_promo_inactive"),
        registered=format_datetime_ru(client.registered_at),
    )
    await edit_banner(
        call.message,
        text,
        banner=get_banner_file("profile-banner"),
        reply_markup=kb_profile(client.primary_city, show_addresses=True),
    )
    await call.answer()


@router.callback_query(F.data == "profile:top_up")
async def show_top_up(call: CallbackQuery, state: FSMContext | None = None):
    if state:
        await state.clear()
    client = await api_client.profile.get_profile(call.from_user.id)
    text = t(
        "profile_top_up_caption",
        balance=f"{getattr(client, 'balance', 0)} ₽",
    )
    await edit_banner(
        call.message,
        text,
        banner=get_banner_file("top-up-banner"),
        reply_markup=kb_top_up_methods(),
    )
    await call.answer()


@router.callback_query(F.data == "top_up:method:card")
async def top_up_method_card(call: CallbackQuery, state: FSMContext):
    await state.set_state(TopUpState.amount)
    await state.update_data(bot_msg_id=call.message.message_id)
    await edit_banner(
        call.message,
        t("top_up_amount_prompt"),
        banner=get_banner_file("top-up-banner"),
        reply_markup=kb_back("back_to_profile", "menu:profile"),
    )
    await call.answer()


@router.message(TopUpState.amount)
async def top_up_process_amount(msg: Message, state: FSMContext, bot: Bot):
    await msg.delete()
    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id") or (msg.message_id - 1)
    raw_amount = (msg.text or "").strip().replace(" ", "").replace("₽", "")
    try:
        amount = int(raw_amount)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await bot_edit_banner(
            bot,
            msg.chat.id,
            bot_msg_id,
            t(
                "top_up_amount_invalid",
                min_amount=f"{MIN_TOP_UP_AMOUNT:,}".replace(",", " "),
                max_amount=f"{MAX_TOP_UP_AMOUNT:,}".replace(",", " "),
            ),
            banner=get_banner_file("top-up-banner"),
            reply_markup=kb_back("back_to_profile", "menu:profile"),
        )
        return

    if amount < MIN_TOP_UP_AMOUNT or amount > MAX_TOP_UP_AMOUNT:
        await bot_edit_banner(
            bot,
            msg.chat.id,
            bot_msg_id,
            t(
                "top_up_amount_limit_error",
                min_amount=f"{MIN_TOP_UP_AMOUNT:,}".replace(",", " "),
                max_amount=f"{MAX_TOP_UP_AMOUNT:,}".replace(",", " "),
            ),
            banner=get_banner_file("top-up-banner"),
            reply_markup=kb_back("back_to_profile", "menu:profile"),
        )
        return

    order_number = uuid.uuid4().hex[:8].upper()
    await state.clear()
    await state.update_data(
        bot_msg_id=bot_msg_id,
        order_number=order_number,
        order_total_sum=amount,
        top_up_amount=amount,
        check_amount=amount,
    )

    card = await api_client.cards.get_suitable_card(amount)
    if card:
        text = t(
            "top_up_card_card_text",
            order_number=order_number,
            price=amount,
            card_number=card.card_number,
        )
        markup = kb_card_payment_with_card(
            order_number,
            send_check_callback=f"top_up:send_check:{order_number}",
            back_callback="menu:profile",
        )
        requisites_snapshot = card.card_number
    else:
        text = t(
            "top_up_card_text",
            order_number=order_number,
            price=amount,
        )
        markup = kb_card_payment(
            order_number,
            back_callback="menu:profile",
        )
        requisites_snapshot = None

    await bot_edit_banner(
        bot,
        msg.chat.id,
        data.get("bot_msg_id", msg.message_id),
        text,
        banner=get_banner_file("payment-method-banner"),
        reply_markup=markup,
    )

    try:
        await api_client.invoices.create_invoice(
            invoice_number=order_number,
            user_id=msg.from_user.id,
            amount=amount,
            purpose="deposit",
            payment_method="Банковская карта",
            order_number=order_number,
            requisites_snapshot=requisites_snapshot,
        )
    except Exception:
        pass

    await emit_log_event(
        "payment_request",
        msg.from_user.id,
        {
            "user_id": msg.from_user.id,
            "first_name": msg.from_user.first_name or "",
            "last_name": msg.from_user.last_name or "",
            "username": msg.from_user.username,
            "order_number": order_number,
            "invoice_number": order_number,
            "model_info": "Пополнение баланса",
            "tariff_plan": "Пополнение баланса",
            "additional": "Нет",
            "meet_info": "Пополнение баланса",
            "payment_method": "Банковская карта",
            "amount": str(amount),
        },
    )


@router.callback_query(F.data.startswith("top_up:send_check:"))
async def top_up_send_check(call: CallbackQuery, state: FSMContext):
    order_number = call.data.split(":")[2]
    data = await state.get_data()
    amount = data.get("top_up_amount") or data.get("order_total_sum") or 0
    await state.set_state(OrderCheckState.waiting_for_check)
    await state.update_data(
        check_order_number=order_number,
        check_purpose="deposit",
        check_bot_msg_id=call.message.message_id,
        check_chat_id=call.message.chat.id,
        order_total_sum=amount,
        top_up_amount=amount,
        check_amount=amount,
    )
    await edit_banner(
        call.message,
        t("models_check_prompt"),
        banner=get_banner_file("send-check-banner"),
        reply_markup=kb_check_prompt(order_number, back_callback="menu:profile"),
    )
    await call.answer()


@router.callback_query(F.data == "profile:orders")
async def show_orders_type(call: CallbackQuery):
    await edit_banner(
        call.message,
        t("profile_orders_caption"),
        banner=get_banner_file("orders-banner"),
        reply_markup=kb_orders_type(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("orders:"))
async def show_orders_list(call: CallbackQuery):
    is_active = call.data == "orders:active"
    orders_response = await api_client.profile.get_orders(
        user_id=call.from_user.id,
        status_filter="active" if is_active else "completed",
    )
    orders = orders_response.items
    if not orders:
        await call.answer(t("profile_orders_empty"), show_alert=True)
        return
    lines = [f"#{order.order_number} — {order.form_snapshot or '—'} ({order.status})" for order in orders[:10]]
    title = t("profile_orders_active_title") if is_active else t("profile_orders_completed_title")
    await edit_banner(
        call.message,
        f"{title}\n\n" + "\n".join(lines),
        banner=get_banner_file("orders-banner"),
        reply_markup=kb_back("back_to_orders", "profile:orders"),
    )
    await call.answer()




@router.callback_query(F.data == "profile:promo")
async def start_promo(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PromoState.code)
    await state.update_data(bot_msg_id=call.message.message_id)
    await edit_banner(
        call.message,
        t("profile_promo_enter"),
        banner=get_banner_file("enter-promo-banner"),
        reply_markup=kb_back("back_to_profile", "menu:profile"),
    )
    await call.answer()


@router.message(PromoState.code)
async def process_promo(msg: Message, state: FSMContext, bot: Bot):
    del bot
    await msg.delete()
    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id") or (msg.message_id - 1)
    code = (msg.text or "").strip()
    if not code:
        return

    promo_result = await api_client.profile.activate_promo(user_id=msg.from_user.id, code=code)
    if not promo_result.applied:
        await bot_edit_banner(
            msg.bot,
            msg.chat.id,
            bot_msg_id,
            t("profile_promo_not_found", code=code),
            banner=get_banner_file("promo-not-found-banner"),
            reply_markup=kb_back("back_to_profile", "menu:profile"),
        )
        return

    await state.clear()
    await bot_edit_banner(
        msg.bot,
        msg.chat.id,
        bot_msg_id,
        t("profile_promo_activated", code=code),
        banner=get_banner_file("promo-activate-banner"),
        reply_markup=kb_back("back_to_profile", "menu:profile"),
    )


@router.callback_query(F.data == "profile:city")
async def show_city_management(call: CallbackQuery):
    client = await api_client.profile.get_profile(call.from_user.id)
    await edit_banner(
        call.message,
        t("profile_city_manage"),
        banner=get_banner_file("choice-city-banner"),
        reply_markup=kb_city_management(client.primary_city, client.secondary_city, client.active_city_slot),
    )
    await call.answer()


@router.callback_query(F.data.regexp(r"^city:switch:\d+$"))
async def switch_city(call: CallbackQuery):
    new_status = int(call.data.split(":")[-1])
    client = await api_client.profile.get_profile(call.from_user.id)
    if new_status == client.active_city_slot:
        await call.answer(t("profile_city_already_active"), show_alert=True)
        return
    target_city = client.primary_city if new_status == 1 else client.secondary_city
    if not target_city:
        await call.answer(t("profile_city_missing"), show_alert=True)
        return
    client = await api_client.clients.switch_city(call.from_user.id, active_city_slot=new_status)
    await edit_banner(
        call.message,
        t("profile_city_manage"),
        banner=get_banner_file("choice-city-banner"),
        reply_markup=kb_city_management(client.primary_city, client.secondary_city, client.active_city_slot),
    )
    await call.answer(t("profile_city_active_answer", city=target_city))


@router.callback_query(F.data == "city:add")
async def add_secondary_city(call: CallbackQuery, state: FSMContext):
    client = await api_client.profile.get_profile(call.from_user.id)
    if not client.primary_city:
        slot = 1
    elif not client.secondary_city:
        slot = 2
    else:
        await call.answer("Все слоты городов уже заполнены.", show_alert=True)
        return

    await state.set_state(CityState.waiting_city)
    await state.update_data(city_slot=slot, bot_msg_id=call.message.message_id, next_route="menu:profile")
    await edit_banner(
        call.message,
        t("profile_city_second_prompt"),
        banner=get_banner_file("choice-city-banner"),
        reply_markup=kb_back("back_to_city", "profile:city"),
    )
    await call.answer()


# ── Inline Query Dispatcher ───────────────────────────────────────────────────

@router.inline_query()
async def handle_profile_inline(query: InlineQuery) -> None:
    raw_text = (query.query or "").strip()
    offset_page = int(query.offset) if query.offset and query.offset.isdigit() else 1
    logger.info("handle_profile_inline received query=%r from user_id=%s, offset=%s", raw_text, query.from_user.id, query.offset)

    if "my_transactions" in raw_text or raw_text.startswith("my_transactions") or raw_text.startswith("transactions"):
        search_text = raw_text
        if "search=" in raw_text:
            search_text = raw_text.split("search=", 1)[1].strip()
        else:
            search_text = raw_text.replace("my_transactions", "").replace("transactions", "").strip()

        try:
            response = await api_client.profile.get_transactions(
                user_id=query.from_user.id,
                query=search_text or None,
                page=offset_page,
                per_page=_PAGE_SIZE,
            )
        except Exception as exc:
            logger.exception("Error getting transactions for user %s: %s", query.from_user.id, exc)
            await query.answer([], cache_time=1, is_personal=True)
            return

        if not response.items:
            await query.answer(
                [],
                cache_time=1,
                is_personal=True,
                switch_pm_text="У Вас еще нет операций",
                switch_pm_parameter="start",
            )
            return

        results = []
        for tx in response.items:
            type_name = {
                "deposit": "Пополнение",
                "balance_payment": "Оплата с баланса",
                "direct_payment": "Прямая оплата",
                "refund": "Возврат",
                "admin_adjust": "Корректировка",
            }.get(tx.type, tx.type)
            sign = "+" if tx.type in ("deposit", "refund") else "-"
            title = f"{sign}{tx.amount} ₽ — {type_name}"
            desc = f"Баланс: {tx.balance_after} ₽ | {tx.description}\n{format_datetime_ru(tx.created_at)}"

            results.append(
                InlineQueryResultArticle(
                    id=f"tx:{tx.id}",
                    title=title,
                    description=desc,
                    thumbnail_url=MY_TRANSACTIONS_SEARCH_ICON,
                    input_message_content=InputTextMessageContent(
                        message_text=f"get_my_transaction_{tx.id}",
                    ),
                )
            )

        has_next = offset_page * _PAGE_SIZE < response.total
        next_offset = str(offset_page + 1) if has_next else ""

        await query.answer(
            results=results,
            cache_time=0,
            is_personal=True,
            next_offset=next_offset,
        )
        return

    if "my_orders" in raw_text or raw_text.startswith("my_orders") or raw_text.startswith("orders"):
        search_text = raw_text
        if "search=" in raw_text:
            search_text = raw_text.split("search=", 1)[1].strip()
        else:
            search_text = raw_text.replace("my_orders", "").replace("orders", "").strip()

        try:
            response = await api_client.profile.get_orders(
                user_id=query.from_user.id,
                query=search_text or None,
                page=offset_page,
                per_page=_PAGE_SIZE,
            )
        except Exception as exc:
            logger.exception("Error getting orders for user %s: %s", query.from_user.id, exc)
            await query.answer([], cache_time=1, is_personal=True)
            return

        if not response.items:
            await query.answer(
                [],
                cache_time=1,
                is_personal=True,
                switch_pm_text="У Вас еще нет заказов",
                switch_pm_parameter="start",
            )
            return

        results = []
        for order in response.items:
            status_name = {
                "pending": "В обработке",
                "completed": "Завершён",
                "rejected": "Отклонён",
            }.get(order.status, order.status)
            title = f"Заказ #{order.order_number}"
            desc = f"{order.form_snapshot or 'Модель'} | {status_name}\n{format_datetime_ru(order.created_at)}"

            results.append(
                InlineQueryResultArticle(
                    id=f"order:{order.order_number}",
                    title=title,
                    description=desc,
                    thumbnail_url=MY_ORDERS_SEARCH_ICON,
                    input_message_content=InputTextMessageContent(
                        message_text=f"get_my_order_{order.order_number}",
                    ),
                )
            )

        has_next = offset_page * _PAGE_SIZE < response.total
        next_offset = str(offset_page + 1) if has_next else ""

        await query.answer(
            results=results,
            cache_time=0,
            is_personal=True,
            next_offset=next_offset,
        )
        return

    if (
        "my_favorites" in raw_text
        or raw_text.startswith("my_favorites")
        or raw_text.startswith("favorites")
        or raw_text.startswith("favs")
    ):
        search_text = raw_text
        if "search=" in raw_text:
            search_text = raw_text.split("search=", 1)[1].strip()
        elif raw_text.startswith("my_favorites"):
            search_text = raw_text[len("my_favorites"):].lstrip("?").strip()
        elif raw_text.startswith("favorites"):
            search_text = raw_text[len("favorites"):].lstrip("?").strip()
        elif raw_text.startswith("favs"):
            search_text = raw_text[len("favs"):].lstrip("?").strip()

        if search_text.startswith("search="):
            search_text = search_text[len("search="):].strip()

        try:
            response = await api_client.profile.get_favorites(
                user_id=query.from_user.id,
                query=search_text or None,
                page=offset_page,
                per_page=_PAGE_SIZE,
            )
        except Exception as exc:
            logger.exception("Error getting favorites for user %s: %s", query.from_user.id, exc)
            await query.answer([], cache_time=1, is_personal=True)
            return

        if not response.items:
            await query.answer(
                [],
                cache_time=1,
                is_personal=True,
                switch_pm_text="У Вас еще нет избранных анкет",
                switch_pm_parameter="start",
            )
            return

        results = []
        for fav in response.items:
            name = fav.name or f"Анкета #{fav.form_code}"
            title = f"{name} (#{fav.form_code})"
            price_text = f"{fav.price_1h} ₽" if fav.price_1h else "—"
            desc = f"{fav.age} лет, рост {fav.height} см | грудь {fav.bust_size}\n1 час: {price_text}"
            thumb = _resolve_photo_thumbnail(fav.photo_url)

            send_id = fav.form_id if fav.form_id else fav.form_code
            results.append(
                InlineQueryResultArticle(
                    id=f"fav:{send_id}",
                    title=title,
                    description=desc,
                    thumbnail_url=thumb,
                    input_message_content=InputTextMessageContent(
                        message_text=f"get_form_{send_id}",
                    ),
                )
            )

        has_next = offset_page * _PAGE_SIZE < response.total
        next_offset = str(offset_page + 1) if has_next else ""

        await query.answer(
            results=results,
            cache_time=0,
            is_personal=True,
            next_offset=next_offset,
        )
        return

    await query.answer([], cache_time=1, is_personal=True)



# ── Message Interceptors from Inline Results ──────────────────────────────────

@router.message(F.chat.type == "private", F.text.regexp(r"^get_my_transaction_(\d+)$"))
async def handle_get_my_transaction(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        tx_id = int((message.text or "").rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return

    try:
        await message.delete()
    except Exception:
        pass

    try:
        tx = await api_client.profile.get_transaction(user_id=message.from_user.id, transaction_id=tx_id)
    except Exception:
        return

    type_name = {
        "deposit": "Пополнение",
        "balance_payment": "Оплата с баланса",
        "direct_payment": "Прямая оплата",
        "refund": "Возврат",
        "admin_adjust": "Корректировка",
    }.get(tx.type, tx.type)
    sign = "+" if tx.type in ("deposit", "refund") else "-"
    text = t(
        "profile_transaction_card",
        id=tx.id,
        amount=f"{sign}{tx.amount} ₽",
        type=type_name,
        description=tx.description,
        balance_after=f"{tx.balance_after} ₽",
        created_at=format_datetime_ru(tx.created_at),
    )

    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id") or (message.message_id - 1)
    if bot_msg_id:
        try:
            res = await bot_edit_banner(
                bot,
                message.chat.id,
                bot_msg_id,
                text,
                banner=get_banner_file("profile-banner"),
                reply_markup=kb_profile_detail_back(),
            )
            if res:
                new_bot_id = res.message_id if hasattr(res, "message_id") else bot_msg_id
                await state.update_data(bot_msg_id=new_bot_id)
                return
        except Exception:
            pass

    sent = await answer_banner(
        message,
        text,
        banner=get_banner_file("profile-banner"),
        reply_markup=kb_profile_detail_back(),
    )
    if sent:
        await state.update_data(bot_msg_id=sent.message_id)


@router.message(F.chat.type == "private", F.text.regexp(r"^get_my_order_([A-Za-z0-9_-]+)$"))
async def handle_get_my_order(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        order_num = (message.text or "").replace("get_my_order_", "", 1).strip()
    except Exception:
        return

    try:
        await message.delete()
    except Exception:
        pass

    try:
        order = await api_client.profile.get_order(user_id=message.from_user.id, order_number=order_num)
    except Exception:
        return

    status_name = {
        "pending": "В обработке",
        "completed": "Завершён",
        "rejected": "Отклонён",
    }.get(order.status, order.status)

    date_str = f"{order.scheduled_day or ''} {order.scheduled_month or ''}".strip() or "—"
    place_str = (
        "У модели"
        if order.meeting_place_type == "at_model"
        else ("У себя" if order.meeting_place_type == "at_client" else (order.meeting_place_type or "—"))
    )

    text = t(
        "profile_order_card",
        order_number=order.order_number,
        model_name=order.form_snapshot or "—",
        tariff=order.tariff_name or "—",
        status=status_name,
        city=order.city_name or "—",
        meeting_date=date_str,
        meeting_time=order.scheduled_time or "—",
        meeting_place=place_str,
        address=order.address_text or "—",
        created_at=format_datetime_ru(order.created_at),
    )

    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id") or (message.message_id - 1)
    if bot_msg_id:
        try:
            res = await bot_edit_banner(
                bot,
                message.chat.id,
                bot_msg_id,
                text,
                banner=get_banner_file("orders-banner"),
                reply_markup=kb_profile_detail_back(),
            )
            if res:
                new_bot_id = res.message_id if hasattr(res, "message_id") else bot_msg_id
                await state.update_data(bot_msg_id=new_bot_id)
                return
        except Exception:
            pass

    sent = await answer_banner(
        message,
        text,
        banner=get_banner_file("orders-banner"),
        reply_markup=kb_profile_detail_back(),
    )
    if sent:
        await state.update_data(bot_msg_id=sent.message_id)


@router.message(F.chat.type == "private", F.text.regexp(r"^get_form_([A-Za-z0-9_-]+)$"))
async def handle_get_form_from_inline(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        form_ref = (message.text or "").replace("get_form_", "", 1).strip()
    except Exception:
        return

    try:
        await message.delete()
    except Exception:
        pass

    if not form_ref:
        return

    # Запоминаем в FSM состоянии, что просмотр анкеты открыт из избранных/профиля
    await state.update_data(model_back_target="menu:profile")

    card = await get_form_card_payload(
        message.from_user.id,
        form_ref,
        photo_idx=0,
        fallback_media=models_banner_media(),
        back_target="menu:profile",
    )
    if not card:
        return
    selected_photo, text, markup = card

    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id") or (message.message_id - 1)

    if bot_msg_id:
        try:
            res = await bot_edit_photo(
                bot,
                message.chat.id,
                bot_msg_id,
                text,
                selected_photo,
                reply_markup=markup,
            )
            if res and hasattr(res, "message_id"):
                await state.update_data(bot_msg_id=res.message_id)
            return
        except Exception:
            pass

    sent = await bot.send_photo(
        chat_id=message.chat.id,
        photo=selected_photo,
        caption=text,
        reply_markup=markup,
    )
    if sent:
        await state.update_data(bot_msg_id=sent.message_id)
