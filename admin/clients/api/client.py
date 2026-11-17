from __future__ import annotations

from .admin import AdminApi


class AdminApiClient:
    def __init__(self) -> None:
        self.admin = AdminApi()

    async def close(self) -> None:
        pass


api_client = AdminApiClient()
