from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt as pyjwt

from backend.core.settings import settings


def create_user_session_token(
    *,
    user_id: int,
    telegram_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    username: str | None = None,
    agreement_accepted: bool = False,
    is_mock: bool = False,
) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=max(1, settings.WEB_APP_SESSION_TTL_HOURS))
    payload = {
        "iss": "web_app",
        "sub": str(user_id),
        "aud": settings.WEB_APP_SESSION_AUDIENCE,
        "iat": now,
        "exp": expires_at,
        "user_id": user_id,
        "telegram_id": telegram_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "agreement_accepted": agreement_accepted,
        "is_mock": is_mock,
    }
    token = pyjwt.encode(payload, settings.WEB_APP_SESSION_SECRET, algorithm="HS256")
    return token, expires_at


def verify_user_session_token(token: str) -> dict:
    return pyjwt.decode(
        token,
        settings.WEB_APP_SESSION_SECRET,
        algorithms=["HS256"],
        audience=settings.WEB_APP_SESSION_AUDIENCE,
        options={"require": ["exp", "iat", "iss", "sub", "aud"]},
    )
