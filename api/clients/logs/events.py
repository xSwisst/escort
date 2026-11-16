from __future__ import annotations

from .base import LogsSection
from .schemas import LogEventRequest, LogEventResponse


class LogsEventsApi(LogsSection):
    async def send(self, event: LogEventRequest) -> LogEventResponse:
        return await self._post("/v1/events", model=LogEventResponse, json=event.model_dump(mode="json"))

    async def info(
        self,
        *,
        event_type: str,
        payload: dict,
        actor_id: int | None = None,
        chat_id: int | None = None,
        message_id: int | None = None,
    ) -> LogEventResponse:
        return await self.send(
            LogEventRequest(
                service="api",
                level="info",
                event_type=event_type,
                payload=payload,
                actor_id=actor_id,
                chat_id=chat_id,
                message_id=message_id,
            )
        )

    async def warning(
        self,
        *,
        event_type: str,
        payload: dict,
        actor_id: int | None = None,
        chat_id: int | None = None,
        message_id: int | None = None,
    ) -> LogEventResponse:
        return await self.send(
            LogEventRequest(
                service="api",
                level="warning",
                event_type=event_type,
                payload=payload,
                actor_id=actor_id,
                chat_id=chat_id,
                message_id=message_id,
            )
        )
