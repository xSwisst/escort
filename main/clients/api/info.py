from __future__ import annotations

from .base import ApiSection
from .schemas import AgreementInfo


class InfoApi(ApiSection):
    async def get_agreement(self, user_id: int) -> AgreementInfo:
        return await self._get("/client/v1/info/agreement", model=AgreementInfo, params={"user_id": user_id})
