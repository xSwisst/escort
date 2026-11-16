from __future__ import annotations

import logging
from typing import Any

from shared.logging import extract_client_payload

from .base import LogsClientError
from .client import logs_client

logger = logging.getLogger(__name__)


async def emit_api_info(
    *,
    event_type: str,
    payload: dict,
    actor_id: int | None = None,
    chat_id: int | None = None,
    message_id: int | None = None,
) -> bool:
    try:
        await logs_client.events.info(
            event_type=event_type,
            payload=payload,
            actor_id=actor_id,
            chat_id=chat_id,
            message_id=message_id,
        )
    except LogsClientError:
        logger.exception("Failed to emit API log event", extra={"event_type": event_type, "payload": payload})
        return False
    return True


async def emit_client_log(
    event_type: str,
    client: Any = None,
    *,
    actor_id: int | None = None,
    chat_id: int | None = None,
    message_id: int | None = None,
    **extra_payload: Any,
) -> bool:
    """
    Единая точка логирования действий клиента в API.
    Автоматически извлекает из объекта client:
    - id (порядковый ID в БД, clients.id)
    - user_id (Telegram ID)
    - first_name, last_name, username
    и объединяет с дополнительными параметрами события.
    """
    payload = extract_client_payload(client, **extra_payload)
    resolved_actor_id = actor_id or payload.get("user_id")
    return await emit_api_info(
        event_type=event_type,
        payload=payload,
        actor_id=resolved_actor_id,
        chat_id=chat_id,
        message_id=message_id,
    )

