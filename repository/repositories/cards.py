from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.cards import Card
from repositories.base import BaseRepository


class CardRepository(BaseRepository[Card]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Card)

    async def get_by_id(self, card_id: int) -> Card | None:
        """Get card by ID"""
        result = await self._session.execute(
            select(Card).where(Card.id == card_id, Card.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def list_cards(self, include_deleted: bool = False) -> list[Card]:
        """List all cards ordered by id descending"""
        query = select(Card)
        if not include_deleted:
            query = query.where(Card.is_deleted == False)
        query = query.order_by(Card.id.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_suitable_card(self, amount: int) -> Card | None:
        """Find an active, non-deleted card suitable for the given payment amount"""
        query = (
            select(Card)
            .where(
                Card.is_active == True,
                Card.is_deleted == False,
                Card.min_amount <= amount,
                Card.max_amount >= amount,
            )
            .order_by(Card.id.desc())
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def create_card(
        self,
        *,
        card_number: str,
        min_amount: int = 0,
        max_amount: int = 1_000_000,
        created_by: str | None = None,
    ) -> Card:
        """Create and persist a new card"""
        card = Card(
            card_number=card_number.strip(),
            min_amount=min_amount,
            max_amount=max_amount,
            is_active=True,
            is_deleted=False,
            created_by=created_by,
        )
        self._session.add(card)
        await self._session.flush()
        await self._session.refresh(card)
        return card

    async def toggle_active(self, card_id: int) -> Card | None:
        """Toggle active status of a card"""
        card = await self.get_by_id(card_id)
        if not card:
            return None
        card.is_active = not card.is_active
        await self._session.flush()
        await self._session.refresh(card)
        return card

    async def soft_delete(self, card_id: int) -> bool:
        """Soft delete a card (hide from list and active payments without breaking foreign keys)"""
        card = await self.get_by_id(card_id)
        if not card:
            return False
        card.is_deleted = True
        card.is_active = False
        await self._session.flush()
        return True
