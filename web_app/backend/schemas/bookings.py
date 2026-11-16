from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class BookingPrepareRequest(BaseModel):
    meeting_date: str = Field(..., alias="meetingDate")
    meeting_time: str = Field(..., alias="meetingTime")
    meeting_place: Literal['model', 'client'] = Field(..., alias="meetingPlace")
    tariff: Literal['1h', '2h', '3h', 'night']
    address_id: int | None = Field(None, alias="addressId")
    additionals: list[int] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class BookingTariffInfo(BaseModel):
    key: Literal['1h', '2h', '3h', 'night']
    amount: int

    class Config:
        populate_by_name = True
        by_alias = True


class BookingAdditionalItem(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        populate_by_name = True
        by_alias = True


class BookingPaymentMethodItem(BaseModel):
    key: Literal['card', 'cash']

    class Config:
        populate_by_name = True
        by_alias = True


class BookingPrepareResponse(BaseModel):
    order_number: str = Field(..., alias="orderNumber")
    model_name: str = Field(..., alias="modelName")
    model_code: str = Field(..., alias="modelCode")
    amount: int
    additional_sum: int = Field(0, alias="additionalSum")
    currency: str = "RUB"
    tariff: BookingTariffInfo
    additionals: list[BookingAdditionalItem] = Field(default_factory=list)
    payment_methods: list[BookingPaymentMethodItem] = Field(default_factory=list, alias="paymentMethods")

    class Config:
        populate_by_name = True
        by_alias = True


class BookingPaymentCardInfo(BaseModel):
    card_number: str = Field(..., alias="cardNumber")
    holder_name: str = Field(..., alias="holderName")
    bank_name: str = Field(..., alias="bankName")

    class Config:
        populate_by_name = True
        by_alias = True


class BookingPaymentRequest(BaseModel):
    payment_method: Literal['card', 'cash'] = Field(..., alias="paymentMethod")

    class Config:
        populate_by_name = True


class BookingPaymentResponse(BaseModel):
    order_number: str = Field(..., alias="orderNumber")
    model_name: str = Field(..., alias="modelName")
    model_code: str = Field(..., alias="modelCode")
    amount: int
    currency: str = "RUB"
    payment_method: Literal['card', 'cash'] = Field(..., alias="paymentMethod")
    status: Literal['card_requisites', 'manual_support', 'cash_unavailable']
    card: BookingPaymentCardInfo | None = None

    class Config:
        populate_by_name = True
        by_alias = True
