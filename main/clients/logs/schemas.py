from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LogEventRequest(BaseModel):
    service: str
    level: str = "info"
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    trace_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: int | None = None
    chat_id: int | None = None
    message_id: int | None = None


class LogEventResponse(BaseModel):
    ok: bool
    delivered: bool
    trace_id: UUID


class HealthResponse(BaseModel):
    ok: bool
    service: str
