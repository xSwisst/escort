from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ClientActivityLogCreateRequest(BaseModel):
    user_id: int
    client_id: int | None = None
    event_type: str
    title: str | None = None
    description: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None


class ClientActivityLogItem(BaseModel):
    id: int
    user_id: int
    client_id: int | None = None
    event_type: str
    title: str
    description: str | None = None
    created_at: datetime


class ClientActivityLogDetailResponse(BaseModel):
    id: int
    user_id: int
    client_id: int | None = None
    event_type: str
    title: str
    description: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ClientActivityLogsListResponse(BaseModel):
    items: list[ClientActivityLogItem] = Field(default_factory=list)
    total: int
    page: int
    per_page: int
    query: str | None = None
