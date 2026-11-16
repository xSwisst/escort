from __future__ import annotations

from core.settings import settings
from shared.http import ServiceClient

from .events import LogsEventsApi
from .health import LogsHealthApi


class ApiLogsClient:
    def __init__(self) -> None:
        self._http = ServiceClient(
            "http://logs:8006",
            settings.API_SECRET_KEY,
            service_name="api",
            target_audience="escort_logs",
        )
        self.events = LogsEventsApi(self._http)
        self.health = LogsHealthApi(self._http)

    async def close(self) -> None:
        await self._http.close()


logs_client = ApiLogsClient()
