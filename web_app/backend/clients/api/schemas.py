from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AgreementInfo(BaseModel):
    agreement_id: str | None = None
    title: str | None = None
    document_url: str | None = None


class ClientIdentity(BaseModel):
    user_id: int
    has_accepted_agreement: bool


class TelegramUserPayload(BaseModel):
    user_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class StartBootstrapResponse(BaseModel):
    client: ClientIdentity
    agreement_required: bool
    agreement: AgreementInfo | None = None
    user: TelegramUserPayload


class ClientCitiesResponse(BaseModel):
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    active_city: str | None = None


class FormListItem(BaseModel):
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
    photos: list[str] = Field(default_factory=list)
    is_favorite: bool = False


class FormsListResponse(BaseModel):
    items: list[FormListItem] = Field(default_factory=list)


class FormCardResponse(FormListItem):
    has_reviews: bool = False
    has_services: bool = False
    has_additionals: bool = False
    has_private_channel: bool = False
    discount_amount: int | None = None


class FormReviewsResponse(BaseModel):
    form_code: str
    form_name: str
    items: list[dict] = Field(default_factory=list)


class FormAdditionalsResponse(BaseModel):
    form_code: str
    items: list[dict] = Field(default_factory=list)


class FormServicesResponse(BaseModel):
    form_code: str
    items: list[dict] = Field(default_factory=list)


class FavoriteToggleResponse(BaseModel):
    is_favorite: bool


class FavoritesResponse(BaseModel):
    items: list[dict] = Field(default_factory=list)


class ProfileResponse(BaseModel):
    user_id: int
    primary_city: str | None = None
    secondary_city: str | None = None
    active_city_slot: int = 1
    city: str | None = None
    rating: float = 0.0
    orders: int = 0
    promo: str | None = None
    registered_at: datetime


class PromoActivateResponse(BaseModel):
    applied: bool
    promo_code: str | None = None


class OrdersResponse(BaseModel):
    items: list[dict] = Field(default_factory=list)


class AddressItem(BaseModel):
    id: int
    title: str
    address: str


class AddressListResponse(BaseModel):
    items: list[AddressItem] = Field(default_factory=list)
