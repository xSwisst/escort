from __future__ import annotations

from .base import LogsSection
from .schemas import HealthResponse


class LogsHealthApi(LogsSection):
    async def check(self) -> HealthResponse:
        return await self._get("/v1/health", model=HealthResponse)
