from __future__ import annotations

from pydantic import BaseModel


class SuitableCardResponse(BaseModel):
    id: int
    card_number: str
    min_amount: int
    max_amount: int
