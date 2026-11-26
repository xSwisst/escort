from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.handlers.models_shared import get_form_card_payload
from bot.keyboards.common import kb_back
from bot.keyboards.models_catalog import (
    kb_additionals_view,
    kb_models_list,
    kb_private_channel_view,
    kb_reviews,
    kb_services_view,
)
from bot.states import CityState
from clients.api import ApiNotFoundError, api_client
from services import validate_city
from shared.bot.utils.media_banner import answer_banner, bot_edit_banner, bot_edit_photo, edit_banner
from utils.helpers import media_refs, models_banner_media

router = Router(name="models_catalog")

_REVIEWS_PER_PAGE = 3


def _build_reviews_page(form_name: str, reviews: list, *, page: int, per_page: int = _REVIEWS_PER_PAGE) -> tuple[str, int, int]:
    if not reviews:
        return t("models_reviews_empty", name=form_name), 1, 1
    total_pages = max(1, (len(reviews) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    chunk = reviews[start:start + per_page]

    lines = [t("models_reviews_title", name=form_name, count=len(reviews))]
    for review in chunk:
        author = escape(review.author or t("models_review_author_fallback"))
        review_date = escape(review.review_date or "")
        body = escape(review.body or "")
        stars = "⭐" * max(int(review.score or 0), 0)
        lines.append(t("models_review_item", stars=stars, author=author, review_date=review_date, body=body))
    return "\n".join(lines), page, total_pages


def _build_additionals_page(addons: list[tuple[str, int]]) -> str:
    lines = [t("models_additionals_title"), ""]
    for name, price in addons:
        lines.append(t("models_additional_item", name=escape(str(name or t("text_dash"))), price=price))
    return "\n".join(lines)


def _build_services_page(services: list[str]) -> str:
    lines = [t("models_services_title"), ""]
    for name in services:
        lines.append(t("models_service_item", name=escape(str(name or t("text_dash")))))
    return "\n".join(lines)


async def _render_model_card(
    call: CallbackQuery,
    code: str,
    *,
    photo_idx: int = 0,
    back_target: str = "menu:models",
    emit_open_log: bool = False,
) -> bool:
    card = await get_form_card_payload(
        call.from_user.id,
        code,
        photo_idx=photo_idx,
        fallback_media=models_banner_media(),
        back_target=back_target,
        emit_open_log=emit_open_log,
    )
    if not card:
        await call.answer(t("model_not_found"), show_alert=True)
        return False
    selected_photo, text, markup = card

    await bot_edit_photo(
        call.bot,
        call.message.chat.id,
        call.message.message_id,
        text,
        selected_photo,
        reply_markup=markup,
    )
    return True


async def _show_reviews_page(call: CallbackQuery, *, code: str, page: int) -> None:
    try:
        reviews_response = await api_client.forms.get_reviews(code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return
    text, current_page, total_pages = _build_reviews_page(reviews_response.form_name, reviews_response.items, page=page)
    await edit_banner(
        call.message,
        text,
        banner=get_banner_file("models-banner"),
        reply_markup=kb_reviews(code, page=current_page, total_pages=total_pages),
    )
    await call.answer()


async def render_models_catalog(
    target: Message,
    user_id: int,
    state: FSMContext,
    *,
    is_edit: bool = True,
) -> None:
    await state.clear()
    await state.update_data(model_back_target="menu:models")
    client = await api_client.clients.get_cities(user_id)
    city_slot = int(getattr(client, "active_city_slot", 1) or 1)
    active_city = client.active_city

    if not active_city:
        await state.set_state(CityState.waiting_city)
        text = t("models_city_prompt")
        banner = get_banner_file("models-banner")
        markup = kb_back("back_to_main", "menu:main")
        if is_edit:
            await state.update_data(city_slot=city_slot, bot_msg_id=target.message_id, next_route="menu:models")
            await edit_banner(target, text, banner=banner, reply_markup=markup)
        else:
            sent = await answer_banner(target, text, banner=banner, reply_markup=markup)
            if sent:
                await state.update_data(city_slot=city_slot, bot_msg_id=sent.message_id, next_route="menu:models")
        return

    forms = (await api_client.forms.list_forms(user_id=user_id, active_city_slot=city_slot)).items
    text = t("models_catalog", count=len(forms))
    banner = get_banner_file("models-banner")
    markup = kb_models_list(forms, page=0)
    if is_edit:
        res = await edit_banner(target, text, banner=banner, reply_markup=markup)
        msg_id = res.message_id if hasattr(res, "message_id") else target.message_id
        await state.update_data(bot_msg_id=msg_id)
    else:
        sent = await answer_banner(target, text, banner=banner, reply_markup=markup)
        if sent:
            await state.update_data(bot_msg_id=sent.message_id)


@router.callback_query(F.data == "menu:models")
async def show_models(call: CallbackQuery, state: FSMContext):
    await render_models_catalog(call.message, call.from_user.id, state, is_edit=True)
    await call.answer()


@router.callback_query(F.data.regexp(r"^models:\d+$"))
async def models_page(call: CallbackQuery, state: FSMContext):
    page = int(call.data.split(":")[1]) - 1
    client = await api_client.clients.get_cities(call.from_user.id)
    forms = (await api_client.forms.list_forms(user_id=call.from_user.id, active_city_slot=client.active_city_slot)).items
    await state.update_data(bot_msg_id=call.message.message_id)
    await call.message.edit_reply_markup(reply_markup=kb_models_list(forms, page=page))
    await call.answer()


_INLINE_MODELS_PAGE_SIZE = 20


@router.inline_query(F.query.startswith("models_list"))
async def handle_models_inline(query: InlineQuery) -> None:
    raw_text = (query.query or "").strip()
    if "search=" in raw_text:
        search_text = raw_text.split("search=", 1)[1].strip()
    else:
        search_text = raw_text[len("models_list"):].lstrip("?").strip()

    offset_page = int(query.offset) if query.offset and query.offset.isdigit() else 1
    client = await api_client.clients.get_cities(query.from_user.id)
    forms = (await api_client.forms.list_forms(user_id=query.from_user.id, active_city_slot=client.active_city_slot)).items

    q = search_text.lower()
    if q:
        forms = [f for f in forms if q in (f.name or "").lower() or q in (f.code or "").lower()]

    total = len(forms)
    if total == 0:
        await query.answer(
            [],
            cache_time=1,
            is_personal=True,
            switch_pm_text=t("models_inline_empty"),
            switch_pm_parameter="models",
        )
        return

    start = (offset_page - 1) * _INLINE_MODELS_PAGE_SIZE
    page_items = forms[start : start + _INLINE_MODELS_PAGE_SIZE]
    results = []
    for form in page_items:
        price_str = f"{form.one_hour_price} ₽" if form.one_hour_price else t("models_inline_price_missing")
        thumb = form.photo_url if form.photo_url and form.photo_url.startswith(("http://", "https://")) else None
        results.append(
            InlineQueryResultArticle(
                id=f"model:{form.code}",
                title=t("models_inline_title", name=form.name, age=form.age),
                description=t(
                    "models_inline_desc",
                    height=form.height,
                    bust_size=form.bust_size,
                    price=price_str,
                ),
                thumbnail_url=thumb,
                input_message_content=InputTextMessageContent(
                    message_text=f"get_model_{form.code}",
                ),
            )
        )

    has_next = offset_page * _INLINE_MODELS_PAGE_SIZE < total
    next_offset = str(offset_page + 1) if has_next else ""
    await query.answer(
        results=results,
        cache_time=0,
        is_personal=True,
        next_offset=next_offset,
        switch_pm_text=t("models_inline_total", count=total),
        switch_pm_parameter="models",
    )


@router.message(F.chat.type == "private", F.text.regexp(r"^get_model_([A-Za-z0-9_-]+)$"))
async def open_model_from_inline(message: Message, state: FSMContext, bot: Bot) -> None:
    code = (message.text or "").replace("get_model_", "", 1).strip()
    try:
        await message.delete()
    except Exception:
        pass
    if not code:
        return

    await state.update_data(model_back_target="menu:models", **{f"photo_idx_{code}": 0})
    card = await get_form_card_payload(
        message.from_user.id,
        code,
        photo_idx=0,
        fallback_media=models_banner_media(),
        back_target="menu:models",
        emit_open_log=True,
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


@router.callback_query(F.data.startswith("model:view:"))
async def view_model(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":")[2]
    await state.update_data(**{f"photo_idx_{code}": 0})
    data = await state.get_data()
    back_target = data.get("model_back_target", "menu:models")
    if await _render_model_card(call, code, photo_idx=0, back_target=back_target, emit_open_log=True):
        await call.answer()


@router.callback_query(F.data.startswith("model:fav:"))
async def toggle_favorite(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":")[2]
    result = await api_client.forms.toggle_favorite(user_id=call.from_user.id, form_code=code)
    await call.answer(t("model_fav_added") if result.is_favorite else t("model_fav_removed"))
    data = await state.get_data()
    back_target = data.get("model_back_target", "menu:models")
    current_idx = int(data.get(f"photo_idx_{code}", 0) or 0)
    await _render_model_card(call, code, photo_idx=current_idx, back_target=back_target)


@router.callback_query(F.data.startswith("model:private:"))
async def view_private_channel(call: CallbackQuery):
    code = call.data.split(":")[2]
    try:
        private_channel = await api_client.forms.get_private_channel(code)
    except ApiNotFoundError:
        await call.answer(t("models_private_channel_unavailable"), show_alert=True)
        return
    await edit_banner(
        call.message,
        t(
            "models_private_channel_caption",
            name=private_channel.name,
            code=private_channel.form_code,
            description=private_channel.description or t("models_private_channel_default_description"),
            price=private_channel.price,
        ),
        banner=get_banner_file("payment-method-banner"),
        reply_markup=kb_private_channel_view(code, payment_available=True),
    )
    await call.answer()



@router.callback_query(F.data.startswith("model:reviews:"))
async def view_reviews(call: CallbackQuery):
    await _show_reviews_page(call, code=call.data.split(":")[2], page=1)


@router.callback_query(F.data.startswith("model:reviews-page:"))
async def view_reviews_page(call: CallbackQuery):
    _, _, code, page = call.data.split(":")
    await _show_reviews_page(call, code=code, page=int(page))


@router.callback_query(F.data.startswith("model:additionals:"))
async def view_additionals(call: CallbackQuery):
    code = call.data.split(":")[2]
    try:
        addons = await api_client.forms.get_additionals(code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return
    if not addons.items:
        await call.answer(t("models_additionals_unavailable"), show_alert=True)
        return
    await edit_banner(
        call.message,
        _build_additionals_page([(item.name, item.price) for item in addons.items]),
        banner=get_banner_file("models-banner"),
        reply_markup=kb_additionals_view(code),
    )
    await call.answer()


@router.callback_query(F.data.startswith("model:services:"))
async def view_services(call: CallbackQuery):
    code = call.data.split(":")[2]
    try:
        services = await api_client.forms.get_services(code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return
    if not services.items:
        await call.answer(t("models_services_unavailable"), show_alert=True)
        return
    await edit_banner(
        call.message,
        _build_services_page([item.name for item in services.items]),
        banner=get_banner_file("models-banner"),
        reply_markup=kb_services_view(code),
    )
    await call.answer()


@router.callback_query(F.data.startswith("model:photo:"))
async def cycle_photo(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = parts[2]
    try:
        form = await api_client.forms.get_form_card(user_id=call.from_user.id, form_code=code)
    except ApiNotFoundError:
        await call.answer(t("model_not_found"), show_alert=True)
        return

    photos = media_refs(form.photos)
    if len(photos) <= 1:
        await call.answer(t("model_no_other_photos"), show_alert=True)
        return

    data = await state.get_data()
    back_target = data.get("model_back_target", "menu:models")
    current_idx = int(data.get(f"photo_idx_{code}", 0) or 0)
    if len(parts) >= 4 and parts[3].isdigit():
        next_idx = max(0, min(len(photos) - 1, int(parts[3]) - 1))
    else:
        next_idx = (current_idx + 1) % len(photos)
    if next_idx == current_idx:
        await call.answer()
        return
    await state.update_data(**{f"photo_idx_{code}": next_idx})
    await _render_model_card(call, code, photo_idx=next_idx, back_target=back_target)
    await call.answer()


@router.message(CityState.waiting_city)
async def process_city(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()

    city_name = await validate_city(msg.text.strip())
    if not city_name:
        await bot_edit_banner(
            msg.bot,
            msg.chat.id,
            data["bot_msg_id"],
            t("models_city_not_found"),
            banner=get_banner_file("models-banner"),
            reply_markup=kb_back("back_to_city", "profile:city")
        )
        return

    slot = int(data.get("city_slot", 1) or 1)
    if await api_client.clients.has_city(msg.from_user.id, city_name):
        await bot_edit_banner(
            msg.bot,
            msg.chat.id,
            data["bot_msg_id"],
            f"⚠️ Город <b>{escape(city_name)}</b> уже добавлен в ваш список. Введите другой город:",
            banner=get_banner_file("choice-city-banner"),
            reply_markup=kb_back("back_to_city", "profile:city"),
        )
        return

    client = await api_client.clients.set_city(msg.from_user.id, city=city_name, slot=slot)
    await api_client.clients.switch_city(msg.from_user.id, active_city_slot=slot)
    await state.clear()

    next_route = data.get("next_route")
    if next_route == "menu:models":
        forms = (await api_client.forms.list_forms(user_id=msg.from_user.id, active_city_slot=slot)).items
        await bot_edit_banner(
            msg.bot,
            msg.chat.id,
            data["bot_msg_id"],
            t("models_catalog", count=len(forms)),
            banner=get_banner_file("models-banner"),
            reply_markup=kb_models_list(forms, page=0),
        )
        return

    if next_route == "menu:profile":
        await bot_edit_banner(
            msg.bot,
            msg.chat.id,
            data["bot_msg_id"],
            t("models_city_set", city_name=city_name),
            banner=get_banner_file("profile-banner"),
            reply_markup=kb_back("back_to_city", "profile:city"),
        )
