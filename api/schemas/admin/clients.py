from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AdminClientListItem(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    avatar_url: str | None = None
    active_city: str | None = None
    is_banned: bool = False
    registered_at: datetime


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


class SetClientBanRequest(BaseModel):
    is_banned: bool


class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1)


class BroadcastButton(BaseModel):
    text: str
    url: str | None = None


class BroadcastRequest(BaseModel):
    audience: str = Field(default="all")  # all, new7, new14, new30
    text: str = Field(min_length=1)
    media_url: str | None = None
    buttons: list[BroadcastButton] = Field(default_factory=list)


class BroadcastResponse(BaseModel):
    sent: int
    failed: int
    total: int
