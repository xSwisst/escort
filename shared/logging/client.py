"""
HTTP client для отправки логов в logs сервис.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from shared.http import ServiceClient

logger = logging.getLogger(__name__)


class EventsAPI:
    """API для отправки событий"""

    def __init__(
        self,
        base_url: str,
        service_name: str,
        timeout: float,
        secret_key: str = "",
        target_audience: str = "escort_logs",
    ):
        self._base_url = base_url.rstrip("/")
        self._service_name = service_name
        self._timeout = timeout
        self._secret_key = secret_key
        self._target_audience = target_audience
        self._service_client: ServiceClient | None = None

        if self._base_url and self._secret_key:
            self._service_client = ServiceClient(
                self._base_url,
                self._secret_key,
                service_name=self._service_name,
                target_audience=self._target_audience,
                timeout=self._timeout,
            )

    async def close(self) -> None:
        if self._service_client:
            await self._service_client.close()

    async def info(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
        actor_id: int | None = None,
        chat_id: int | None = None,
        message_id: int | None = None,
    ) -> bool:
        """Отправляет информационное событие"""
        try:
            event_data: dict[str, Any] = {
                "service": self._service_name,
                "level": "info",
                "event_type": event_type,
                "payload": payload,
            }
            if actor_id is not None:
                event_data["actor_id"] = actor_id
            if chat_id is not None:
                event_data["chat_id"] = chat_id
            if message_id is not None:
                event_data["message_id"] = message_id

            if self._service_client:
                await self._service_client.post("/v1/events", json=event_data)
                return True

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/v1/events",
                    json=event_data,
                )
                response.raise_for_status()
                return True
        except Exception:
            logger.exception("Failed to send log event to %s", self._base_url)
            return False


class LogsClient:
    """Клиент для отправки событий в logs сервис"""

    def __init__(
        self,
        base_url: str,
        service_name: str = "unknown",
        timeout: float = 5.0,
        secret_key: str = "",
        target_audience: str = "escort_logs",
    ) -> None:
        self._base_url = (base_url or "").rstrip("/")
        self._service_name = service_name
        self._timeout = timeout
        self.events = EventsAPI(
            self._base_url,
            self._service_name,
            self._timeout,
            secret_key=secret_key,
            target_audience=target_audience,
        )

    async def close(self) -> None:
        await self.events.close()

    async def send_event(
        self,
        event_type: str,
        user_id: int,
        data: dict[str, Any],
    ) -> bool:
        """
        Отправляет событие в logs сервис.
        """
        return await self.events.info(
            event_type=event_type,
            payload=data,
            actor_id=user_id,
        )
