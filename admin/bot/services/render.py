from __future__ import annotations

import html
from typing import Any

from bot.assets.texts import t
from shared.utils.date import format_datetime_ru


def build_panel_text(
    total_clients: int,
    total_forms: int = 0,
    total_promos: int = 0,
    total_agreements: int = 0,
    forms_city_1: int = 0,
    forms_city_2: int = 0,
    bot_name: str = "ESCORT V1",
    bot_link_text: str = "@escort_bot",
    service_status: str = "Работает",
    service_status_emoji: str = "🟢",
    referral_link: str = "Недоступно",
    today: int = 0,
    month: int = 0,
) -> str:
    return t(
        "panel_caption",
        bot_name=html.escape(str(bot_name or "ESCORT V1")),
        bot_link_text=html.escape(str(bot_link_text or "Недоступно")),
        service_status=service_status,
        service_status_emoji=service_status_emoji,
        referral_link=html.escape(str(referral_link or "Недоступно")),
        today=today,
        month=month,
        total_clients=total_clients,
        total_forms=total_forms,
        forms_city_1=forms_city_1,
        forms_city_2=forms_city_2,
        total_promos=total_promos,
        total_agreements=total_agreements,
    )


def build_model_card_text(form) -> str:
    def _format_price(val: int | None) -> str:
        return f"{val} ₽" if val is not None else "—"

    return t(
        "va_model_card",
        code=form.code,
        name=form.name,
        age=form.age,
        height=form.height,
        tits=form.bust_size,
        bust_size=form.bust_size,
        city=f"Город {form.city_slot}",
        city_slot=form.city_slot,
        sort_order=form.sort_order,
        price_one_hours=_format_price(form.one_hour_price),
        price_two_hours=_format_price(form.two_hour_price),
        price_three_hours=_format_price(form.three_hour_price),
        price_night=_format_price(form.overnight_price),
        price_1h=_format_price(form.one_hour_price),
        price_2h=_format_price(form.two_hour_price),
        price_3h=_format_price(form.three_hour_price),
        caption=form.caption or "Без описания",
        rating=f"{float(form.rating):.1f}" if getattr(form, "rating", None) is not None else "—",
        orders=str(getattr(form, "orders", 0) or 0),
        document=t("word_yes") if form.has_medical_certificate else t("word_no"),
        verification=t("word_yes") if form.is_verified else t("word_no"),
        private_channel=getattr(form, "public_channel_url", None) or "—",
        dynamic=t("word_static"),
        visibility=t("word_visible") if form.is_visible else t("word_hidden"),
        visible_badge="🟢 Включена" if form.is_visible else "🔴 Выключена",
        verified_badge="✅ Есть" if form.is_verified else "❌ Нет",
        medical_badge="✅ Есть" if form.has_medical_certificate else "❌ Нет",
        photos_count=len(form.photos or []),
    )


def build_client_list_text(response) -> str:
    total_pages = max(1, (response.total + response.per_page - 1) // response.per_page)
    if not response.items:
        return t("panel_results_empty", query=response.query or "-")
    lines = [
        t(
            "client_list_item",
            user_id=item.user_id,
            full_name=(" ".join(part for part in [item.first_name, item.last_name] if part).strip() or t("client_name_missing")),
            username=f"@{item.username}" if item.username else t("client_username_missing"),
            city=item.active_city or t("client_city_missing"),
        )
        for item in response.items
    ]
    return t(
        "panel_results_caption",
        query=response.query or "-",
        total=response.total,
        page=response.page,
        total_pages=total_pages,
        items="\n".join(lines),
    )


def build_client_card_text(client) -> str:
    full_name = " ".join(part for part in [client.first_name, client.last_name] if part).strip() or t("client_name_missing")
    username_str = f"@{client.username}" if client.username else t("client_username_missing")
    agreement_title = client.title or t("client_agreement_missing")
    if client.has_accepted_agreement:
        agreement_str = f"{agreement_title} (✅ Принято)"
    else:
        agreement_str = f"{agreement_title} (❌ Не принято)"

    last_active_dt = getattr(client, "last_active_at", None)
    last_active_str = format_datetime_ru(last_active_dt) if last_active_dt else "—"
    rating_val = getattr(client, "rating", 0.0)
    rating_str = f"{float(rating_val):.1f}" if rating_val is not None else "0.0"

    return t(
        "va_client_card",
        client_name=full_name,
        full_name=full_name,
        username=username_str,
        client_id=client.user_id,
        user_id=client.user_id,
        balance=int(getattr(client, "balance", 0) or 0),
        orders=int(getattr(client, "orders_count", 0) or 0),
        rating=rating_str,
        addresses=int(getattr(client, "addresses_count", 0) or 0),
        favorites=int(getattr(client, "favorites_count", 0) or 0),
        city=client.active_city or client.primary_city or t("client_city_missing"),
        primary_city=client.primary_city or t("client_city_missing"),
        secondary_city=client.secondary_city or t("client_city_missing"),
        active_city=client.active_city or t("client_city_missing"),
        promo=client.promo or t("client_promo_missing"),
        title=agreement_title,
        agreement=agreement_str,
        has_accepted_agreement=t("word_yes") if client.has_accepted_agreement else t("word_no"),
        ban=t("word_ban_yes") if client.is_banned else t("word_ban_no"),
        ban_status=t("client_ban_enabled") if client.is_banned else t("client_ban_disabled"),
        last_active=last_active_str,
        registered=format_datetime_ru(client.registered_at),
        registered_at=format_datetime_ru(client.registered_at),
    )


def build_log_detail_text(
    log: Any,
    client: Any = None,
) -> str:
    user_id = log.user_id
    first_name = ""
    last_name = ""
    username = ""
    client_db_id = str(log.client_id) if log.client_id is not None else "—"

    if client:
        first_name = client.first_name or ""
        last_name = client.last_name or ""
        username = client.username or ""
        if str(getattr(client, "id", "")).strip():
            client_db_id = str(client.id)

    payload = log.payload or {}
    if not first_name and not last_name:
        first_name = payload.get("first_name") or ""
        last_name = payload.get("last_name") or ""
    if not username:
        username = payload.get("username") or ""

    name_display = f"{first_name} {last_name}".strip() or payload.get("client_name") or t("client_name_missing")
    username_display = f"@{username}" if username else t("client_username_missing")

    details_lines: list[str] = []
    if "city" in payload:
        details_lines.append(t("log_detail_city", city=html.escape(str(payload["city"]))))
    if "old_city" in payload and "new_city" in payload:
        details_lines.append(t("log_detail_city_change_old", old_city=html.escape(str(payload["old_city"]))))
        details_lines.append(t("log_detail_city_change_new", new_city=html.escape(str(payload["new_city"]))))
    if "address_name" in payload or "title" in payload:
        addr_title = payload.get("address_name") or payload.get("title")
        details_lines.append(t("log_detail_address_name", address_name=html.escape(str(addr_title))))
    if "address" in payload or "full_address" in payload:
        addr_val = payload.get("address") or payload.get("full_address")
        details_lines.append(t("log_detail_address", address=html.escape(str(addr_val))))
    if "order_number" in payload or "order_id" in payload:
        ord_val = payload.get("order_number") or payload.get("order_id")
        details_lines.append(t("log_detail_order_number", order_number=html.escape(str(ord_val))))
    if "model_name" in payload or "model_info" in payload:
        m_val = payload.get("model_name") or payload.get("model_info")
        details_lines.append(t("log_detail_model", model=html.escape(str(m_val))))
    if "tariff" in payload or "tariff_plan" in payload:
        t_val = payload.get("tariff") or payload.get("tariff_plan")
        details_lines.append(t("log_detail_tariff", tariff=html.escape(str(t_val))))
    if "amount" in payload:
        details_lines.append(t("log_detail_amount", amount=html.escape(str(payload["amount"]))))
    if "payment_method" in payload:
        details_lines.append(t("log_detail_payment_method", payment_method=html.escape(str(payload["payment_method"]))))
    if "place" in payload or "meet_info" in payload:
        p_val = payload.get("place") or payload.get("meet_info")
        details_lines.append(t("log_detail_place", place=html.escape(str(p_val))))
    if "code" in payload or "form_code" in payload:
        c_val = payload.get("code") or payload.get("form_code")
        details_lines.append(t("log_detail_code", code=html.escape(str(c_val))))
    if "text" in payload or "message_text" in payload:
        txt_val = payload.get("text") or payload.get("message_text")
        details_lines.append(t("log_detail_message", message=html.escape(str(txt_val))))

    if not details_lines and log.description:
        details_lines.append(t("log_detail_info", info=html.escape(log.description)))

    details_block = "\n".join(details_lines) if details_lines else "—"
    date_time = format_datetime_ru(log.created_at)

    return t(
        "client_log_detail_card",
        title=html.escape(log.title),
        log_id=log.id,
        client_db_id=html.escape(client_db_id),
        name_display=html.escape(name_display),
        user_id=user_id,
        username_display=html.escape(username_display),
        details_block=details_block,
        date_time=date_time,
    )

