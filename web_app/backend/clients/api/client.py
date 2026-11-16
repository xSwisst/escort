from __future__ import annotations

from backend.core.settings import settings
from shared.http import ServiceClient

from .client_v1 import ClientV1Api


class BackendApiClient:
    def __init__(self) -> None:
        self._http = ServiceClient(
            settings.API_BASE_URL,
            settings.API_SECRET_KEY,
            service_name="web_app",
            target_audience=settings.API_AUDIENCE,
        )
        self.client_v1 = ClientV1Api(self._http)

    async def close(self) -> None:
        await self._http.close()


api_client = BackendApiClient()
