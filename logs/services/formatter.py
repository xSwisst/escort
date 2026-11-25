from __future__ import annotations

from datetime import datetime, timedelta, timezone
import html
import json
import logging
import re
from typing import Any, TYPE_CHECKING
import httpx

from assets.texts import t
from core.settings import settings
from shared.auth import create_service_token
from shared.utils.date import format_datetime_ru

if TYPE_CHECKING:
    from schemas import LogEventRequest

logger = logging.getLogger(__name__)

MSK_TZ = timezone(timedelta(hours=3))

_admin_bot_username: str | None = None
_client_db_id_cache: dict[str, str] = {}


def _get_auth_headers() -> dict[str, str]:
    if not settings.API_SECRET_KEY:
        return {}
    token = create_service_token(
        secret_key=settings.API_SECRET_KEY,
        issuer=settings.API_AUDIENCE,
        audience=settings.API_TARGET_AUDIENCE,
        ttl_hours=1,
    )
    return {"Authorization": f"Bearer {token}"}


async def _get_admin_bot_username() -> str:
    global _admin_bot_username
    if _admin_bot_username:
        return _admin_bot_username
    try:
        url = f"{settings.API_BASE_URL.rstrip('/')}/internal/v1/admin-bot/username"
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, headers=_get_auth_headers())
            if resp.status_code == 200:
                data = resp.json()
                username = data.get("username") or ""
                if username:
                    _admin_bot_username = username
                    return username
    except Exception as exc:
        logger.debug("Failed to get admin bot username: %s", exc)
    return _admin_bot_username or ""


async def _resolve_client_id_from_api(user_id: str) -> str | None:
    if not user_id:
        return None
    if user_id in _client_db_id_cache:
        return _client_db_id_cache[user_id]
    try:
        url = f"{settings.API_BASE_URL.rstrip('/')}/internal/v1/clients/by-user-id/{user_id}"
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, headers=_get_auth_headers())
            if resp.status_code == 200:
                data = resp.json()
                client_id = data.get("id")
                if client_id is not None:
                    db_id_str = str(client_id)
                    _client_db_id_cache[user_id] = db_id_str
                    return db_id_str
    except Exception as exc:
        logger.debug("Failed to resolve client db id for user_id=%s: %s", user_id, exc)
    return None


def _format_amount(val: Any) -> str:
    if val is None or val == "":
        return "0"
    val_str = str(val).strip()
    try:
        num = float(val_str.replace(" ", "").replace(",", "."))
        if num.is_integer():
            return f"{int(num):,}".replace(",", " ")
        return f"{num:,.2f}".replace(",", " ")
    except ValueError:
        return _escape(val_str)


def _format_price_field(val: Any) -> str:
    if val is None or val == "" or str(val).strip() in ("—", "None"):
        return "—"
    return _format_amount(val)


def _payload_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)


def _escape(val: Any) -> str:
    if val is None:
        return ""
    return html.escape(str(val))


def _meta_block(event: LogEventRequest) -> str:
    lines: list[str] = []
    if event.actor_id is not None:
        lines.append(t("meta_actor_id", actor_id=event.actor_id))
    if event.chat_id is not None:
        lines.append(t("meta_chat_id", chat_id=event.chat_id))
    if event.message_id is not None:
        lines.append(t("meta_message_id", message_id=event.message_id))
    lines.append(t("meta_trace_id", trace_id=event.trace_id))
    lines.append(t("meta_occurred_at", occurred_at=event.occurred_at.isoformat()))
    return "\n".join(lines)


async def format_event_message(event: LogEventRequest, log_id: int | None = None) -> str:
    payload: dict[str, Any] = dict(event.payload or {})
    payload_json = _payload_json(payload)

    service_label = t(f"service_{event.service.value}")
    if service_label == f"service_{event.service.value}":
        service_label = event.service.value

    level_label = t(f"level_{event.level.value}")
    if level_label == f"level_{event.level.value}":
        level_label = event.level.value.upper()

    # Дата и время: "20 сентября 2026, в 12:52"
    date_time = format_datetime_ru(event.occurred_at)

    # Идентификатор клиента
    raw_user_id = (
        payload.get("user_id")
        or payload.get("client_id")
        or payload.get("uid")
        or event.actor_id
        or event.chat_id
    )
    user_id_str = str(raw_user_id) if raw_user_id is not None else ""

    # Database ID клиента (clients.id), а не telegram user_id
    raw_db_id = payload.get("id") or payload.get("client_db_id")
    id_str = str(raw_db_id) if raw_db_id is not None and str(raw_db_id).strip() not in ("", "None", "—") else "—"

    if id_str == "—" and user_id_str:
        resolved = await _resolve_client_id_from_api(user_id_str)
        if resolved:
            id_str = resolved

    # Имя и фамилия
    raw_first_name = payload.get("first_name")
    raw_last_name = payload.get("last_name")
    raw_client_name = payload.get("client_name") or payload.get("name")

    first_name = str(raw_first_name or "").strip()
    last_name = str(raw_last_name or "").strip()

    if raw_client_name:
        client_name = str(raw_client_name).strip()
    elif first_name or last_name:
        client_name = f"{first_name} {last_name}".strip()
    else:
        client_name = "Не указано"

    if not first_name:
        first_name = client_name

    # Юзернейм
    raw_username = payload.get("username") or payload.get("client_username") or payload.get("uname")
    if raw_username:
        clean_username = str(raw_username).lstrip("@").strip()
        username = clean_username
        username_display = f"@{clean_username}"
    else:
        username = "Отсутствует"
        username_display = "Отсутствует"

    # Юзернейм админ-бота для диплинка
    admin_bot_username = await _get_admin_bot_username()

    # Диплинк формата: t.me/{username}?start=open_client_{id}
    # Важно: <tg-emoji> должен быть ВНЕ тега <a>, иначе Telegram парсер аннулирует custom_emoji
    # и отображает обычный текстовый fallback ✨!
    if admin_bot_username and id_str != "—":
        client_deeplink = f"https://t.me/{admin_bot_username}?start=open_client_{id_str}"
        client_info_header = (
            f'<blockquote><b><tg-emoji emoji-id="5276371072642493917">✨</tg-emoji> <a href="{client_deeplink}">› Информация о клиенте #{_escape(id_str)}</a></b></blockquote>'
        )
    else:
        client_deeplink = ""
        client_info_header = (
            f'<blockquote><b><tg-emoji emoji-id="5276371072642493917">✨</tg-emoji> › Информация о клиенте #{_escape(id_str)}</b></blockquote>'
        )

    # Диплинк формата: t.me/{username}?start=open_model_{code_or_id}
    raw_model_ref = payload.get("code") or payload.get("form_id") or payload.get("form_code")
    model_ref_str = str(raw_model_ref).strip() if raw_model_ref is not None else ""
    if admin_bot_username and model_ref_str and model_ref_str not in ("—", "None", ""):
        model_deeplink = f"https://t.me/{admin_bot_username}?start=open_model_{model_ref_str}"
    else:
        model_deeplink = ""

    # Диплинк формата: t.me/{username}?start=get_log_{log_id}
    if admin_bot_username and log_id is not None:
        log_deeplink = f"https://t.me/{admin_bot_username}?start=get_log_{log_id}"
    else:
        log_deeplink = ""

    # Реферальный deeplink блок
    deeplink = payload.get("deeplink")
    if deeplink:
        deeplink_block = (
            f"\n<blockquote><b> › Реферальная ссылка</b></blockquote>\n"
            f"Код: <code>{_escape(deeplink)}</code>\n"
        )
    else:
        deeplink_block = ""
    # Заголовок для payment_request (Заявка на пополнение vs Заявка на оплату)
    meet_lower = str(payload.get("meet_info") or "").lower()
    model_lower = str(payload.get("model_info") or "").lower()
    is_topup = "пополнение" in meet_lower or "пополнение" in model_lower
    payment_request_title = "Заявка на пополнение" if is_topup else "Заявка на оплату"

    # Блок информации об админе (воркере)
    raw_admin_id = payload.get("admin_id")
    if raw_admin_id not in (None, "", "—"):
        raw_admin_un = payload.get("admin_username")
        if raw_admin_un:
            admin_un_display = f"@{str(raw_admin_un).lstrip('@').strip()}"
        else:
            admin_un_display = "Отсутствует"
        admin_block = t(
            "admin_info_block",
            admin_id=_escape(raw_admin_id),
            admin_name=_escape(payload.get("admin_name") or "Не указано"),
            admin_telegram_id=_escape(payload.get("admin_telegram_id") or "—"),
            admin_username_display=_escape(admin_un_display),
        ).strip()
    else:
        admin_block = ""

    # Блок информации о клиенте (для fallback)
    if user_id_str:
        client_info_block = (
            f"\n{client_info_header}\n"
            f"Имя: <b>{_escape(client_name)}</b>\n"
            f"ID: <code>{_escape(user_id_str)}</code>\n"
            f"Username: <b>{_escape(username_display)}</b>\n"
        )
    else:
        client_info_block = ""

    # Предзаполнение всех остальных частых полей с экранированием
    values: dict[str, Any] = {
        # Системные метаданные
        "service": event.service.value,
        "service_label": service_label,
        "level": event.level.value,
        "level_label": level_label,
        "event_type": event.event_type,
        "trace_id": event.trace_id,
        "occurred_at": event.occurred_at.isoformat(),
        "actor_id": event.actor_id or "",
        "chat_id": event.chat_id or "",
        "message_id": event.message_id or "",
        "date_time": date_time,
        "payment_request_title": payment_request_title,
        "payload_json": payload_json,
        "payload_block": t("payload_block", payload_json=payload_json),
        "client_info_block": client_info_block,
        "admin_block": admin_block,
        "deeplink_block": deeplink_block,
        # Клиент
        "user_id": _escape(user_id_str),
        "client_id": _escape(user_id_str),
        "id": _escape(id_str),
        "client_info_header": client_info_header,
        "client_deeplink": client_deeplink,
        "model_deeplink": model_deeplink,
        "admin_bot_username": admin_bot_username,
        "first_name": _escape(first_name),
        "last_name": _escape(last_name),
        "client_name": _escape(client_name),
        "name": _escape(client_name),
        "username": _escape(username),
        "username_display": _escape(username_display),
        # Действия и параметры
        "city": _escape(payload.get("city") or "Не указан"),
        "old_city": _escape(payload.get("old_city") or "—"),
        "new_city": _escape(payload.get("new_city") or payload.get("city") or "—"),
        "address_name": _escape(payload.get("address_name") or payload.get("title") or "—"),
        "address": _escape(payload.get("address") or payload.get("full_address") or "—"),
        "amount": _format_amount(payload.get("amount") or payload.get("total_sum") or payload.get("price") or "0"),
        "order_number": _escape(payload.get("order_number") or payload.get("order_id") or "—"),
        "order_id": _escape(payload.get("order_id") or payload.get("order_number") or "—"),
        "code": _escape(payload.get("code") or payload.get("form_code") or payload.get("promo_code") or "—"),
        "form_code": _escape(payload.get("form_code") or payload.get("code") or "—"),
        "form_id": _escape(payload.get("form_id") or payload.get("code") or "—"),
        "model_name": _escape(payload.get("model_name") or payload.get("model_info") or "—"),
        "model_info": _escape(payload.get("model_info") or payload.get("model_name") or "—"),
        "tariff": _escape(payload.get("tariff") or payload.get("tariff_plan") or "—"),
        "tariff_plan": _escape(payload.get("tariff_plan") or payload.get("tariff") or "—"),
        "additional": _escape(payload.get("additional") or payload.get("additionals") or "Нет"),
        "additionals": _escape(payload.get("additionals") or payload.get("additional") or "Нет"),
        "meet_info": _escape(payload.get("meet_info") or payload.get("place") or "—"),
        "place": _escape(payload.get("place") or payload.get("meet_info") or "—"),
        "meeting_time": _escape(payload.get("meeting_time") or payload.get("meeting_date") or date_time),
        "payment_method": _escape(payload.get("payment_method") or payload.get("method") or "—"),
        "promocode_id": _escape(payload.get("promocode_id") or payload.get("promo_id") or "—"),
        "promo_type": _escape(payload.get("promo_type") or "Скидка"),
        "usage_limit": _escape(payload.get("usage_limit") or "—"),
        "remaining_uses": _escape(payload.get("remaining_uses") or "—"),
        "expires_at": _escape(payload.get("expires_at") or "Бессрочно"),
        "admin_name": _escape(payload.get("admin_name") or "Администратор"),
        "admin_id": _escape(payload.get("admin_id") or "—"),
        "topic_id": _escape(payload.get("topic_id") or "—"),
        "age": _escape(payload.get("age") or "—"),
        "height": _escape(payload.get("height") or "—"),
        "breast": _escape(payload.get("breast") or "—"),
        "caption": _escape(payload.get("caption") or ""),
        "price_1h": _format_price_field(payload.get("price_1h") or payload.get("price_one_hours")),
        "price_2h": _format_price_field(payload.get("price_2h") or payload.get("price_two_hours")),
        "price_3h": _format_price_field(payload.get("price_3h") or payload.get("price_three_hours")),
        "price_night": _format_price_field(payload.get("price_night")),
        "verification": _escape(payload.get("verification") or "—"),
        "medical_certificate": _escape(payload.get("medical_certificate") or "—"),
        "author": _escape(payload.get("author") or "Аноним"),
        "rating": _escape(payload.get("rating") or payload.get("score") or "—"),
        "review_text": _escape(payload.get("review_text") or payload.get("text") or "—"),
        "audience": _escape(payload.get("audience") or "—"),
        "total": _escape(payload.get("total") or "0"),
        "sent": _escape(payload.get("sent") or "0"),
        "failed": _escape(payload.get("failed") or "0"),
        "text": _escape(payload.get("text") or payload.get("message_text") or "—"),
    }

    # Добавляем все остальные сырые ключи из payload (с экранированием)
    for k, v in payload.items():
        if k not in values:
            values[k] = _escape(v)

    # Если для данного типа события нет шаблона в messages.yaml, пропускаем отправку
    if t(event.event_type) == event.event_type:
        return ""
    text = t(event.event_type, **values).strip()

    if admin_block and "{admin_block}" not in t(event.event_type):
        date_marker = "<i>Дата и время:"
        if date_marker in text:
            text = text.replace(date_marker, f"{admin_block}\n\n{date_marker}", 1)
        else:
            text = f"{text}\n\n{admin_block}"

    # Оборачиваем верхний заголовок события в тег <a> с диплинком на лог (эмодзи остается снаружи <a>)
    if log_deeplink:
        pattern = r'(<blockquote><b><tg-emoji emoji-id="\d+">[^<]+</tg-emoji>)\s*›\s*([^<]+)(</b></blockquote>)'

        def _wrap_top_header(match: re.Match) -> str:
            prefix = match.group(1)
            title_text = match.group(2).strip()
            suffix = match.group(3)
            return f'{prefix} <a href="{log_deeplink}">› {title_text}</a>{suffix}'

        text = re.sub(pattern, _wrap_top_header, text, count=1)

    # Оборачиваем строчку заголовка клиента в тег <a> с диплинком (эмодзи вне <a> для сохранения Telegram Premium эмодзи)
    if client_deeplink and id_str != "—":
        escaped_id = _escape(id_str)
        unwrapped_header = f'<blockquote><b><tg-emoji emoji-id="5276371072642493917">✨</tg-emoji> › Информация о клиенте #{escaped_id}</b></blockquote>'
        wrapped_header = f'<blockquote><b><tg-emoji emoji-id="5276371072642493917">✨</tg-emoji> <a href="{client_deeplink}">› Информация о клиенте #{escaped_id}</a></b></blockquote>'
        if unwrapped_header in text:
            text = text.replace(unwrapped_header, wrapped_header)

    # Оборачиваем строчку заголовка анкеты/модели в тег <a> с диплинком
    if model_deeplink:
        form_id_str = values.get("form_id", "")
        unwrapped_form_header = f'<blockquote><b><tg-emoji emoji-id="5278317079374633314">✨</tg-emoji> › Информация об анкете #{form_id_str}</b></blockquote>'
        wrapped_form_header = f'<blockquote><b><tg-emoji emoji-id="5278317079374633314">✨</tg-emoji> <a href="{model_deeplink}">› Информация об анкете #{form_id_str}</a></b></blockquote>'
        if unwrapped_form_header in text:
            text = text.replace(unwrapped_form_header, wrapped_form_header)

        unwrapped_model_header = f'<blockquote><b><tg-emoji emoji-id="5278317079374633314">✨</tg-emoji> › Информация о модели #{form_id_str}</b></blockquote>'
        wrapped_model_header = f'<blockquote><b><tg-emoji emoji-id="5278317079374633314">✨</tg-emoji> <a href="{model_deeplink}">› Информация о модели #{form_id_str}</a></b></blockquote>'
        if unwrapped_model_header in text:
            text = text.replace(unwrapped_model_header, wrapped_model_header)

    return text
