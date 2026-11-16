from __future__ import annotations

from pydantic import Field

from .common import ApiSchema


class FormListItem(ApiSchema):
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


class FormsListResponse(ApiSchema):
    items: list[FormListItem] = Field(default_factory=list)


class ReviewItem(ApiSchema):
    author: str | None = None
    review_date: str | None = None
    body: str | None = None
    score: int = 0


class FormReviewsResponse(ApiSchema):
    form_code: str
    form_name: str
    items: list[ReviewItem] = Field(default_factory=list)


class FormAdditionalItem(ApiSchema):
    name: str
    price: int


class FormAdditionalsResponse(ApiSchema):
    form_code: str
    items: list[FormAdditionalItem] = Field(default_factory=list)


class FormServiceItem(ApiSchema):
    name: str


class FormServicesResponse(ApiSchema):
    form_code: str
    items: list[FormServiceItem] = Field(default_factory=list)


class FormPrivateChannelResponse(ApiSchema):
    form_code: str
    name: str
    price: int
    description: str | None = None


class FormCardResponse(ApiSchema):
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


class FavoriteToggleResponse(ApiSchema):
    is_favorite: bool
