from __future__ import annotations

import logging
from typing import Any

from shared.logging import resolve_client_meta
from .client import logs_client

logger = logging.getLogger(__name__)


async def emit_log_event(
    event_type: str,
    user_id: int,
    data: dict[str, Any] | None = None,
) -> bool:
    """
    Отправляет событие в logs сервис.
    """
    if data is None:
        data = {}

    if "user_id" not in data:
        data["user_id"] = user_id

    if not data.get("id") or not data.get("admin_id"):
        meta = await resolve_client_meta(user_id)
        for key, value in meta.items():
            if value is not None and not data.get(key):
                data[key] = value

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
            extra={"event_type": event_type, "user_id": user_id},
        )
        return False
