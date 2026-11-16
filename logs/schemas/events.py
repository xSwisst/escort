from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ServiceName(str, Enum):
    api = "api"
    main = "main"
    support = "support"
    admin = "admin"
    web_app = "web_app"
    photos = "photos"
    logs = "logs"


class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class LogEventRequest(BaseModel):
    service: ServiceName
    level: LogLevel = LogLevel.info
    event_type: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
    trace_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: int | None = None
    chat_id: int | None = None
    message_id: int | None = None

    @field_validator("event_type")
    @classmethod
    def normalize_event_type(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("event_type must not be empty")
        return normalized


class LogEventResponse(BaseModel):
    ok: bool = True
    delivered: bool
    trace_id: UUID


class HealthResponse(BaseModel):
    ok: bool = True
    service: str
