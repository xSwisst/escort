from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .common import ApiSchema


class ProfileResponse(ApiSchema):
    id: int | None = None
    user_id: int
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    city: str | None = None
    rating: float = 0.0
    orders: int = 0
    balance: int = 0
    promo: str | None = None
    registered_at: datetime


class OrderItem(ApiSchema):
    id: int | None = None
    order_number: str
    form_snapshot: str | None = None
    city_name: str | None = None
    tariff_name: str | None = None
    status: str
    created_at: datetime
    scheduled_month: str | None = None
    scheduled_day: str | None = None
    scheduled_time: str | None = None
    meeting_place_type: str | None = None
    address_text: str | None = None


class OrdersResponse(ApiSchema):
    items: list[OrderItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 10


class TransactionItem(ApiSchema):
    id: int
    user_id: int
    invoice_id: int | None = None
    type: str
    amount: int
    balance_after: int
    purpose: str | None = None
    order_number: str | None = None
    description: str
    created_at: datetime


class TransactionsResponse(ApiSchema):
    items: list[TransactionItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 10


class FavoriteItem(ApiSchema):
    form_id: int = 0
    form_code: str
    name: str = ""
    age: int = 0
    height: int = 0
    bust_size: int = 0
    price_1h: int | None = None
    city_slot: int = 1
    photo_url: str | None = None
    photos: list[str] = Field(default_factory=list)


class FavoritesResponse(ApiSchema):
    items: list[FavoriteItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 10


class PromoActivateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=64)


class PromoActivateResponse(ApiSchema):
    applied: bool
    promo_code: str | None = None

