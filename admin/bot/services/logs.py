"""
Интеграция с logs сервисом для отправки событий.
"""
from __future__ import annotations

from clients.logs import logs_client
from shared.logging import emit_event


async def emit_admin_info(
    *,
    event_type: str,
    payload: dict,
    actor_id: int | None = None,
    chat_id: int | None = None,
    message_id: int | None = None,
) -> bool:
    """
    Отправляет событие в logs сервис от admin сервиса.
    
    Args:
        event_type: Тип события
        payload: Дополнительные данные события
        actor_id: ID пользователя
        chat_id: ID чата
        message_id: ID сообщения
        
    Returns:
        True если успешно отправлено
    """
    return await emit_event(
        logs_client=logs_client,
        service_name="admin",
        event_type=event_type,
        payload=payload,
        actor_id=actor_id,
        chat_id=chat_id,
        message_id=message_id,
    )
