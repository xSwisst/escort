from __future__ import annotations

from pydantic import BaseModel


class SupportMessageResponse(BaseModel):
    id: int
    user_id: int
    forum_chat_id: int
    topic_id: int
    support_message_id: int
    user_message_id: int
    original_support_message_id: int | None = None
    original_user_message_id: int | None = None


class SupportMessageCreateRequest(BaseModel):
    user_id: int
    forum_chat_id: int
    topic_id: int
    support_message_id: int
    user_message_id: int
    original_support_message_id: int | None = None
    original_user_message_id: int | None = None
