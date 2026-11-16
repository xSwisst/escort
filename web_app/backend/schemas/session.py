from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class TelegramUserData(BaseModel):
    telegram_id: int = Field(..., alias="telegramId")
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    username: str | None = None
    photo_url: str | None = Field(None, alias="photoUrl")

    class Config:
        populate_by_name = True
        by_alias = True


class SessionClientData(BaseModel):
    worker_id: int | None = Field(None, alias="workerId")
    agreement_accepted: bool = Field(..., alias="agreementAccepted")
    is_banned: bool = Field(False, alias="isBanned")

    class Config:
        populate_by_name = True
        by_alias = True


class SessionEnvironmentData(BaseModel):
    telegram: bool
    mock: bool = False

    class Config:
        populate_by_name = True
        by_alias = True


class WebAppSessionResponse(BaseModel):
    session_token: str = Field(..., alias="sessionToken")
    expires_at: datetime = Field(..., alias="expiresAt")
    user: TelegramUserData
    client: SessionClientData
    environment: SessionEnvironmentData

    class Config:
        populate_by_name = True
        by_alias = True


class CreateSessionRequest(BaseModel):
    init_data: str | None = Field(None, alias='initData')

    class Config:
        populate_by_name = True


class MockUserPayload(BaseModel):
    telegram_id: int = Field(..., alias="telegramId")
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    username: str | None = None
    photo_url: str | None = Field(None, alias="photoUrl")

    class Config:
        populate_by_name = True


class CreateMockSessionRequest(BaseModel):
    user: MockUserPayload
