from __future__ import annotations

import logging
from typing import Any

from .client import logs_client

logger = logging.getLogger(__name__)


_client_id_cache: dict[int, int] = {}


async def _resolve_client_db_id(user_id: int) -> int | None:
    if user_id in _client_id_cache:
        return _client_id_cache[user_id]
    try:
        from clients.api import api_client

        profile = await api_client.profile.get_profile(user_id)
        if profile and profile.id:
            _client_id_cache[user_id] = profile.id
            return profile.id
    except Exception as exc:
        logger.debug("Failed to resolve client db_id for user_id=%s: %s", user_id, exc)
    return None


async def emit_log_event(
    event_type: str,
    user_id: int,
    data: dict[str, Any] | None = None,
) -> bool:
    """
    Отправляет событие в logs сервис.
    
    Args:
        event_type: Тип события (new_user, add_city, new_order и т.д.)
        user_id: ID пользователя
        data: Дополнительные данные события
    """
    if data is None:
        data = {}

    if "user_id" not in data:
        data["user_id"] = user_id

    if not data.get("id"):
        db_id = await _resolve_client_db_id(user_id)
        if db_id:
            data["id"] = db_id

    try:
        await logs_client.send_event(
            event_type=event_type,
            user_id=user_id,
            data=data,
        )
        return True
    except Exception:
        logger.exception(
            "Failed to emit log event",
            extra={"event_type": event_type, "user_id": user_id}
        )
        return False
