from __future__ import annotations

import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qsl
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def validate_telegram_init_data(
    init_data: str,
    *,
    bot_token: str,
    max_age_seconds: int = 86400,
) -> dict:
    """Validate Telegram Web App init_data and return user payload."""
    if not init_data:
        raise ValueError("Missing Telegram initData")

    pairs = dict(parse_qsl(str(init_data or ""), keep_blank_values=True))
    provided_hash = str(pairs.pop("hash", "") or "").strip()

    if bot_token and provided_hash:
        data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
        secret = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
        computed_hash = hmac.new(
            secret,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(computed_hash, provided_hash):
            logger.warning(f"Telegram initData signature mismatch! Computed: {computed_hash}, Provided: {provided_hash}")
            raise ValueError("Invalid Telegram initData signature")
    elif not bot_token:
        logger.warning("BOT_TOKEN is not configured in API settings, skipping signature check")

    auth_date_raw = str(pairs.get("auth_date", "") or "").strip()
    if auth_date_raw.isdigit() and max_age_seconds > 0:
        auth_date = int(auth_date_raw)
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if now_ts - auth_date > max_age_seconds:
            logger.warning(f"Telegram initData expired (age: {now_ts - auth_date}s > {max_age_seconds}s)")

    try:
        user_payload = json.loads(str(pairs.get("user") or "{}"))
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid Telegram user payload") from exc

    telegram_id = int(user_payload.get("id") or 0)
    if telegram_id <= 0:
        raise ValueError("Telegram user id is missing")

    return {
        "id": telegram_id,
        "first_name": str(user_payload.get("first_name") or "").strip() or "User",
        "last_name": str(user_payload.get("last_name") or "").strip() or None,
        "username": str(user_payload.get("username") or "").strip() or None,
        "photo_url": str(user_payload.get("photo_url") or "").strip() or None,
    }
