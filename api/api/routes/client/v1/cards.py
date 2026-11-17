from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from repository.repositories.cards import CardRepository
from schemas.client.cards import SuitableCardResponse

router = APIRouter(prefix="/cards", tags=["client-cards"])


@router.get("/suitable", response_model=SuitableCardResponse | None)
async def get_suitable_card(
    amount: int = Query(..., ge=0, description="Payment amount in rubles"),
    session: AsyncSession = Depends(service_session),
) -> SuitableCardResponse | None:
    """Find an active card matching limits for the given amount"""
    repo = CardRepository(session)
    card = await repo.get_suitable_card(amount)
    if not card:
        return None
    return SuitableCardResponse(
        id=card.id,
        card_number=card.card_number,
        min_amount=card.min_amount,
        max_amount=card.max_amount,
    )
