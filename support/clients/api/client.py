from __future__ import annotations

from core.settings import settings
from shared.http import ServiceClient

from .support import SupportApi


class SupportApiClient:
    def __init__(self) -> None:
        self._http = ServiceClient(
            settings.API_BASE_URL,
            settings.API_SECRET_KEY,
            service_name="support",
            target_audience=settings.API_AUDIENCE,
        )
        self.support = SupportApi(self._http)

    async def close(self) -> None:
        await self._http.close()


api_client = SupportApiClient()
