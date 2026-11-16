from __future__ import annotations

from core.settings import settings
from shared.http import ServiceClient

from .admin import AdminApi


class AdminApiClient:
    def __init__(self) -> None:
        self._http = ServiceClient(
            settings.API_BASE_URL,
            settings.API_SECRET_KEY,
            service_name="admin",
            target_audience=settings.API_AUDIENCE,
        )
        self.admin = AdminApi(self._http)

    async def close(self) -> None:
        await self._http.close()


api_client = AdminApiClient()
