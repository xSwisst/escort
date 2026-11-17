from __future__ import annotations

from services.payments import PaymentService
from shared.bot.session import resolve_session
from .schemas import SuitableCardResponse


class CardsApi:
    async def get_suitable_card(self, amount: int) -> SuitableCardResponse | None:
        """Find an active card suitable for the given payment amount"""
        async with resolve_session() as session:
            ps = PaymentService(session)
            card = await ps.get_suitable_card(amount)
            if not card:
                return None
            return SuitableCardResponse(
                id=card.id,
                card_number=card.card_number,
                bank_name=card.bank_name,
                payment_system=card.payment_system,
            )
