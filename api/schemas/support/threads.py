from __future__ import annotations

from pydantic import BaseModel


class SupportThreadResponse(BaseModel):
    user_id: int
    forum_chat_id: int
    topic_id: int
    info_message_id: int | None = None
    is_banned: bool = False


class SupportThreadLookupResponse(SupportThreadResponse):
    pass


class SupportThreadUpsertRequest(BaseModel):
    forum_chat_id: int
    topic_id: int
    info_message_id: int | None = None


class SupportThreadBanRequest(BaseModel):
    is_banned: bool
