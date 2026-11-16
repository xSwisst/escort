from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .common import ApiSchema


class CreateInvoiceRequest(ApiSchema):
    invoice_number: str = Field(..., max_length=32)
    user_id: int
    amount: int = Field(..., ge=0)
    purpose: str = Field(default="deposit", max_length=32)
    payment_method: str = Field(default="manual_card", max_length=32)
    order_id: int | None = None
    order_number: str | None = Field(default=None, max_length=32)
    form_code: str | None = Field(default=None, max_length=64)
    requisites_snapshot: str | None = None
    comment: str | None = Field(default=None, max_length=256)


class InvoiceResponse(ApiSchema):
    id: int
    invoice_number: str
    user_id: int
    amount: int
    purpose: str
    status: str
    payment_method: str
    order_id: int | None = None
    order_number: str | None = None
    form_code: str | None = None
    requisites_snapshot: str | None = None
    comment: str | None = None
    created_at: datetime
    paid_at: datetime | None = None
