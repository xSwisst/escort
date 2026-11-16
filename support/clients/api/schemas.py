from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AgreementItem(BaseModel):
    agreement_id: str
    title: str
    document_url: str | None = None


class AgreementsResponse(BaseModel):
    items: list[AgreementItem] = Field(default_factory=list)


class ActionStatusResponse(BaseModel):
    ok: bool = True


class MessageCountResponse(BaseModel):
    count: int = 0


class SupportClientSummary(BaseModel):
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


class SupportThread(BaseModel):
    user_id: int
    forum_chat_id: int
    topic_id: int
    info_message_id: int | None = None
    is_banned: bool = False


class SupportMessage(BaseModel):
    id: int
    user_id: int
    forum_chat_id: int
    topic_id: int
    support_message_id: int
    user_message_id: int
    original_support_message_id: int | None = None
    original_user_message_id: int | None = None
