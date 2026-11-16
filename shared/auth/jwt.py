from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt as pyjwt


def create_service_token(
    secret_key: str,
    *,
    issuer: str,
    audience: str | None = None,
    ttl_hours: int = 24,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "iss": issuer,
        "sub": issuer,
        "iat": now,
        "exp": now + timedelta(hours=ttl_hours),
    }
    if audience:
        payload["aud"] = audience
    return pyjwt.encode(payload, secret_key, algorithm="HS256")


def verify_token(
    token: str,
    secret_key: str,
    *,
    audience: str | None = None,
    issuer: str | None = None,
) -> dict:
    options: dict = {"require": ["exp", "iat", "iss", "sub"]}
    kwargs: dict = {"algorithms": ["HS256"]}
    if audience:
        kwargs["audience"] = audience
    else:
        options["verify_aud"] = False
    if issuer:
        kwargs["issuer"] = issuer
    return pyjwt.decode(token, secret_key, options=options, **kwargs)
