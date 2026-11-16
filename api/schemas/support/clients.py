from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SupportClientBootstrapRequest(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class SupportClientSummaryResponse(BaseModel):
    id: int | None = None
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    promo: str | None = None
    agreement_id: str | None = None
    title: str | None = None
    document_url: str | None = None
    is_banned: bool = False
    forum_chat_id: int | None = None
    topic_id: int | None = None
    info_message_id: int | None = None
    registered_at: datetime
