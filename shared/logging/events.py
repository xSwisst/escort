"""Shared logging utilities for emitting events to logs service."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def emit_event(
    *,
    logs_client: Any,
    service_name: str,
    event_type: str,
    payload: dict,
    actor_id: int | None = None,
    chat_id: int | None = None,
    message_id: int | None = None,
) -> bool:
    """
    Emit a log event to the logs service.

    Args:
        logs_client: LogsClient instance (from clients.logs)
        service_name: Service name for logging context (e.g., "main", "support", "admin")
        event_type: Event type identifier
        payload: Event payload data
        actor_id: Optional actor (user) ID
        chat_id: Optional Telegram chat ID
        message_id: Optional Telegram message ID

    Returns:
        True if event was emitted successfully, False otherwise
    """
    try:
        await logs_client.events.info(
            event_type=event_type,
            payload=payload,
            actor_id=actor_id,
            chat_id=chat_id,
            message_id=message_id,
        )
    except Exception:
        logger.exception(
            f"Failed to emit {service_name} log event",
            extra={
                "service": service_name,
                "event_type": event_type,
                "payload": payload,
            },
        )
        return False
    return True
