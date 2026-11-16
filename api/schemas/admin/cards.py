from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CreateCardRequest(BaseModel):
    card_number: str = Field(..., min_length=12, max_length=64, description="Card number")
    min_amount: int = Field(default=0, ge=0, description="Minimum order amount")
    max_amount: int = Field(default=1_000_000, ge=0, description="Maximum order amount")
    created_by: str | None = Field(default=None, description="Admin identifier who created the card")


class CardResponse(BaseModel):
    id: int
    card_number: str
    min_amount: int
    max_amount: int
    is_active: bool
    is_deleted: bool
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime


class CardsListResponse(BaseModel):
    items: list[CardResponse]
    total: int
