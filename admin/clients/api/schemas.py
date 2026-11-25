from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ActionStatusResponse(BaseModel):
    ok: bool = True


class AgreementItem(BaseModel):
    agreement_id: str
    title: str
    document_url: str | None = None


class AgreementsResponse(BaseModel):
    items: list[AgreementItem] = Field(default_factory=list)


class AdminClientListItem(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    avatar_url: str | None = None
    active_city: str | None = None
    is_banned: bool = False
    registered_at: datetime


AdminClientItem = AdminClientListItem


class AdminClientListResponse(BaseModel):
    items: list[AdminClientListItem] = Field(default_factory=list)
    total: int
    page: int
    per_page: int
    query: str | None = None


class AdminClientDetailResponse(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    active_city: str | None = None
    promo: str | None = None
    has_accepted_agreement: bool = False
    agreement_id: str | None = None
    title: str | None = None
    document_url: str | None = None
    is_banned: bool = False
    registered_at: datetime


# ── Forms (Models) ───────────────────────────────────────────────────────────

class FormListItem(BaseModel):
    code: str
    name: str
    age: int
    height: int
    bust_size: int
    one_hour_price: int | None = None
    two_hour_price: int | None = None
    three_hour_price: int | None = None
    overnight_price: int | None = None
    city_slot: int = 1
    sort_order: int = 0
    is_visible: bool = False
    is_verified: bool = False
    has_medical_certificate: bool = False
    photo_count: int = 0
    created_at: datetime


class FormDetailResponse(BaseModel):
    code: str
    name: str
    age: int
    height: int
    bust_size: int
    caption: str | None = None
    one_hour_price: int | None = None
    two_hour_price: int | None = None
    three_hour_price: int | None = None
    overnight_price: int | None = None
    city_slot: int = 1
    sort_order: int = 0
    is_visible: bool = False
    is_verified: bool = False
    has_medical_certificate: bool = False
    rating: float | None = None
    orders: int = 0
    public_channel_url: str | None = None
    photos: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None


class FormsListResponse(BaseModel):
    items: list[FormListItem] = Field(default_factory=list)


# ── Reviews ──────────────────────────────────────────────────────────────────

class ReviewItem(BaseModel):
    id: int
    form_code: str
    author: str
    review_date: str
    body: str
    score: int
    created_at: datetime


class ReviewsListResponse(BaseModel):
    items: list[ReviewItem] = Field(default_factory=list)


# ── Services ─────────────────────────────────────────────────────────────────

class ServiceItem(BaseModel):
    id: int
    form_code: str
    name: str
    created_at: datetime


class ServicesListResponse(BaseModel):
    items: list[ServiceItem] = Field(default_factory=list)


# ── Additionals ──────────────────────────────────────────────────────────────

class AdditionalItem(BaseModel):
    id: int
    form_code: str
    name: str
    price: int
    created_at: datetime


class AdditionalsListResponse(BaseModel):
    items: list[AdditionalItem] = Field(default_factory=list)


# ── Promos ───────────────────────────────────────────────────────────────────

class PromoItem(BaseModel):
    name: str
    discount: int
    created_at: datetime


class PromosListResponse(BaseModel):
    items: list[PromoItem] = Field(default_factory=list)


# ── Broadcast ────────────────────────────────────────────────────────────────

class BroadcastResponse(BaseModel):
    sent: int = 0
    failed: int = 0
    total: int = 0
    total_queued: int = 0
    success: bool = True


class AdminInfo(BaseModel):
    id: int
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime | None = None


class MainBotInfo(BaseModel):
    is_alive: bool = False
    username: str | None = None
    full_name: str | None = None


class WorkerClientStats(BaseModel):
    today: int = 0
    month: int = 0
    all: int = 0


# ── Cards ────────────────────────────────────────────────────────────────────

class CardItem(BaseModel):
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
    items: list[CardItem] = Field(default_factory=list)
    total: int = 0


# ── Client Activity Logs ─────────────────────────────────────────────────────

class AdminClientLogItem(BaseModel):
    id: int
    user_id: int
    client_id: int | None = None
    event_type: str
    title: str
    description: str | None = None
    created_at: datetime


class AdminClientLogsResponse(BaseModel):
    items: list[AdminClientLogItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 10
    query: str | None = None


class AdminClientLogDetailResponse(BaseModel):
    id: int
    user_id: int
    client_id: int | None = None
    event_type: str
    title: str
    description: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

