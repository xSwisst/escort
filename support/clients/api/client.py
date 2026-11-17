from __future__ import annotations

from .support import SupportApi


class SupportApiClient:
    def __init__(self) -> None:
        self.support = SupportApi()

    async def close(self) -> None:
        pass


api_client = SupportApiClient()
