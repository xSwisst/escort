from __future__ import annotations

from pydantic import BaseModel, Field

from .common import AgreementInfo, ClientIdentity


class TelegramUserPayload(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class StartBootstrapRequest(BaseModel):
    user: TelegramUserPayload | None = None
    init_data: str | None = None


class StartBootstrapResponse(BaseModel):
    client: ClientIdentity
    agreement_required: bool
    agreement: AgreementInfo | None = None
    user: TelegramUserPayload


class AcceptAgreementRequest(BaseModel):
    user_id: int


class SetCityRequest(BaseModel):
    city: str = Field(min_length=1, max_length=128)
    slot: int = Field(default=1, ge=1, le=2)


class SwitchCityRequest(BaseModel):
    active_city_slot: int = Field(ge=1, le=2)
