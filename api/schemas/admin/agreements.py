from __future__ import annotations

from pydantic import BaseModel, Field


class AgreementItem(BaseModel):
    agreement_id: str
    title: str
    document_url: str | None = None


class AgreementsResponse(BaseModel):
    items: list[AgreementItem] = Field(default_factory=list)


class SetClientAgreementRequest(BaseModel):
    agreement_id: str = Field(min_length=1, max_length=64)


class CreateAgreementRequest(BaseModel):
    agreement_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=256)
    document_url: str | None = None
