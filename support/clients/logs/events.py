from __future__ import annotations

from shared.logging import resolve_client_meta
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
        enriched = dict(payload or {})
        uid = enriched.get("user_id") or actor_id
        if uid and (not enriched.get("id") or not enriched.get("admin_id")):
            meta = await resolve_client_meta(int(uid))
            for key, value in meta.items():
                if value is not None and not enriched.get(key):
                    enriched[key] = value
        return await self.send(
            LogEventRequest(
                service="support",
                level="info",
                event_type=event_type,
                payload=enriched,
                actor_id=actor_id,
                chat_id=chat_id,
                message_id=message_id,
            )
        )
