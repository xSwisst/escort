"""
Unified logging helper for emitting events to the logs service.

This consolidates duplicate logging code across main, support, and admin services.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


def extract_client_payload(client: Any = None, **extra: Any) -> dict[str, Any]:
    """
    Extracts client identification fields for logging:
    - id: DB primary key (clients.id)
    - user_id: Telegram user ID
    - first_name, last_name, username
    And merges with extra keyword arguments.
    """
    payload: dict[str, Any] = {}
    if client is not None:
        if isinstance(client, dict):
            payload = {
                "id": client.get("id"),
                "user_id": client.get("user_id"),
                "admin_id": client.get("admin_id"),
                "first_name": client.get("first_name") or "",
                "last_name": client.get("last_name") or "",
                "username": client.get("username"),
            }
        else:
            admin_obj = getattr(client, "admin", None)
            admin_name = ""
            if admin_obj is not None:
                admin_name = f"{getattr(admin_obj, 'first_name', '') or ''} {getattr(admin_obj, 'last_name', '') or ''}".strip()
            payload = {
                "id": getattr(client, "id", None),
                "user_id": getattr(client, "user_id", None),
                "admin_id": getattr(client, "admin_id", None),
                "admin_telegram_id": getattr(admin_obj, "telegram_id", None) if admin_obj is not None else None,
                "admin_username": getattr(admin_obj, "username", None) if admin_obj is not None else None,
                "admin_name": admin_name or None,
                "first_name": getattr(client, "first_name", "") or "",
                "last_name": getattr(client, "last_name", "") or "",
                "username": getattr(client, "username", None),
            }
    payload.update(extra)
    return payload


async def emit_event(
    logs_client: Any,
    service_name: str,
    *,
    event_type: str,
    payload: dict,
    actor_id: int | None = None,
    chat_id: int | None = None,
    message_id: int | None = None,
    logger: logging.Logger | None = None,
) -> bool:
    """
    Emit an event to the logs service.

    Args:
        logs_client: The logs client instance to use
        service_name: Name of the service emitting the event (e.g., "main", "support", "admin")
        event_type: Type of event being logged
        payload: Event data
        actor_id: Optional user/admin ID who triggered the event
        chat_id: Optional Telegram chat ID
        message_id: Optional Telegram message ID
        logger: Optional logger instance for error reporting

    Returns:
        True if the event was successfully emitted, False otherwise
    """
    try:
        await logs_client.events.info(
            event_type=event_type,
            payload=payload,
            actor_id=actor_id,
            chat_id=chat_id,
            message_id=message_id,
        )
        return True
    except Exception as e:
        if logger:
            logger.exception(
                f"Failed to emit {service_name} log event",
                extra={
                    "event_type": event_type,
                    "payload": payload,
                    "error": str(e),
                },
            )
        return False
