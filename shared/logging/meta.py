from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_client_meta_cache: dict[int, dict[str, Any]] = {}


async def resolve_client_meta(user_id: int) -> dict[str, Any]:
    """Resolve client DB id and assigned worker (admin) metadata for log payloads."""
    cached = _client_meta_cache.get(user_id)
    if cached and cached.get("admin_id") is not None:
        return cached
    try:
        from repository.repositories.clients import ClientRepository
        from shared.bot.session import resolve_session

        async with resolve_session() as session:
            client = await ClientRepository(session).get(user_id, include_admin=True)
            if client:
                meta: dict[str, Any] = {
                    "id": client.id,
                    "admin_id": client.admin_id,
                }
                if client.admin is not None:
                    admin_name = f"{client.admin.first_name or ''} {client.admin.last_name or ''}".strip()
                    meta["admin_telegram_id"] = client.admin.telegram_id
                    meta["admin_username"] = client.admin.username
                    meta["admin_name"] = admin_name or client.admin.username or f"#{client.admin.id}"
                _client_meta_cache[user_id] = meta
                return meta
    except Exception as exc:
        logger.debug("Failed to resolve client meta for user_id=%s: %s", user_id, exc)
    return cached or {}
