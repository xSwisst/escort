from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AgreementInfo(BaseModel):
    agreement_id: str | None = None
    title: str | None = None
    document_url: str | None = None


class ActionStatusResponse(BaseModel):
    ok: bool = True


class ClientIdentity(BaseModel):
    user_id: int
    has_accepted_agreement: bool


class ClientCities(BaseModel):
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    active_city: str | None = None


class StartBootstrapResponse(BaseModel):
    client: ClientIdentity
    agreement_required: bool
    agreement: AgreementInfo | None = None


class FormListItem(BaseModel):
    code: str
    name: str
    age: int


class FormsListResponse(BaseModel):
    items: list[FormListItem] = Field(default_factory=list)


class ReviewItem(BaseModel):
    author: str | None = None
    review_date: str | None = None
    body: str | None = None
    score: int = 0


class FormReviewsResponse(BaseModel):
    form_code: str
    form_name: str
    items: list[ReviewItem] = Field(default_factory=list)


class FormAdditionalItem(BaseModel):
    name: str
    price: int


class FormAdditionalsResponse(BaseModel):
    form_code: str
    items: list[FormAdditionalItem] = Field(default_factory=list)


class FormServiceItem(BaseModel):
    name: str


class FormServicesResponse(BaseModel):
    form_code: str
    items: list[FormServiceItem] = Field(default_factory=list)


class FormPrivateChannelResponse(BaseModel):
    form_code: str
    name: str
    price: int
    description: str | None = None


class FormCard(BaseModel):
    code: str
    name: str
    age: int
    height: int
    bust_size: int
    one_hour_price: int | None = None
    two_hour_price: int | None = None
    three_hour_price: int | None = None
    overnight_price: int | None = None
    caption: str | None = None
    is_verified: bool = False
    has_medical_certificate: bool = False
    rating: float | None = None
    orders: int = 0
    public_channel_url: str | None = None
    photos: list[str] = Field(default_factory=list)
    is_favorite: bool = False
    has_reviews: bool = False
    has_services: bool = False
    has_additionals: bool = False
    has_private_channel: bool = False
    discount_amount: int | None = None


class FavoriteToggleResponse(BaseModel):
    is_favorite: bool


class ProfileResponse(BaseModel):
    id: int | None = None
    user_id: int
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    city: str | None = None
    rating: float = 0.0
    orders: int = 0
    balance: int = 0
    promo: str | None = None
    registered_at: datetime


class OrderItem(BaseModel):
    id: int | None = None
    order_number: str
    form_snapshot: str | None = None
    city_name: str | None = None
    tariff_name: str | None = None
    status: str
    created_at: datetime
    scheduled_month: str | None = None
    scheduled_day: str | None = None
    scheduled_time: str | None = None
    meeting_place_type: str | None = None
    address_text: str | None = None


class OrdersResponse(BaseModel):
    items: list[OrderItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 10


class TransactionItem(BaseModel):
    id: int
    user_id: int
    invoice_id: int | None = None
    type: str
    amount: int
    balance_after: int
    purpose: str | None = None
    order_number: str | None = None
    description: str
    created_at: datetime


class TransactionsResponse(BaseModel):
    items: list[TransactionItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 10


class FavoriteItem(BaseModel):
    form_id: int = 0
    form_code: str
    name: str = ""
    age: int = 0
    height: int = 0
    bust_size: int = 0
    price_1h: int | None = None
    city_slot: int = 1
    photo_url: str | None = None
    photos: list[str] = Field(default_factory=list)


class FavoritesResponse(BaseModel):
    items: list[FavoriteItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 10


class PromoActivateResponse(BaseModel):
    applied: bool
    promo_code: str | None = None


class AddressItem(BaseModel):
    id: int
    title: str
    address: str


class AddressListResponse(BaseModel):
    items: list[AddressItem] = Field(default_factory=list)


class InvoiceItem(BaseModel):
    id: int
    invoice_number: str
    user_id: int
    amount: int
    purpose: str
    status: str
    payment_method: str
    order_number: str | None = None
    form_code: str | None = None
    requisites_snapshot: str | None = None
    comment: str | None = None
    created_at: datetime
    paid_at: datetime | None = None


class SuitableCardResponse(BaseModel):
    id: int
    card_number: str
    min_amount: int
    max_amount: int
