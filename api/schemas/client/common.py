from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ApiSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ActionStatusResponse(ApiSchema):
    ok: bool = True


class AgreementInfo(ApiSchema):
    agreement_id: str | None = None
    title: str | None = None
    document_url: str | None = None


class ClientIdentity(ApiSchema):
    user_id: int
    has_accepted_agreement: bool


class ClientCitiesResponse(ApiSchema):
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    active_city: str | None = None
