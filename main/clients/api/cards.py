from __future__ import annotations

from .base import ApiSection
from .schemas import SuitableCardResponse


class CardsApi(ApiSection):
    async def get_suitable_card(self, amount: int) -> SuitableCardResponse | None:
        """Find an active card suitable for the given payment amount"""
        try:
            return await self._get(
                "/client/v1/cards/suitable",
                model=SuitableCardResponse,
                params={"amount": amount},
            )
        except Exception:
            return None
