from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .common import ApiSchema


# ── Form schemas ──────────────────────────────────────────────────────────


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
    city_slot: int = 1
    sort_order: int = 0
    is_visible: bool = False
    is_verified: bool = False
    has_medical_certificate: bool = False
    photo_count: int = 0
    created_at: datetime


class FormsListResponse(ApiSchema):
    items: list[FormListItem] = Field(default_factory=list)


class FormDetailResponse(ApiSchema):
    code: str
    name: str
    age: int
    height: int
    bust_size: int
    caption: str | None = None
    one_hour_price: int | None = None
    two_hour_price: int | None = None
    three_hour_price: int | None = None
    overnight_price: int | None = None
    city_slot: int = 1
    sort_order: int = 0
    is_visible: bool = False
    is_verified: bool = False
    has_medical_certificate: bool = False
    rating: float | None = None
    orders: int = 0
    public_channel_url: str | None = None
    photos: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None


class CreateFormRequest(ApiSchema):
    name: str = Field(min_length=1, max_length=50, description="Имя модели")
    age: int = Field(ge=18, le=99, description="Возраст (18-99)")
    height: int = Field(ge=140, le=220, description="Рост в см (140-220)")
    bust_size: int = Field(ge=0, le=10, description="Размер груди (0-10)")
    caption: str | None = Field(default=None, max_length=256, description="Описание анкеты")
    one_hour_price: int | None = Field(default=None, ge=0, description="Цена за 1 час (руб)")
    two_hour_price: int | None = Field(default=None, ge=0, description="Цена за 2 часа (руб)")
    three_hour_price: int | None = Field(default=None, ge=0, description="Цена за 3 часа (руб)")
    overnight_price: int | None = Field(default=None, ge=0, description="Цена за ночь (руб)")
    city_slot: int = Field(default=1, ge=1, le=2, description="Слот города (1 или 2)")
    sort_order: int = Field(default=0, ge=0, description="Порядковый номер при сортировке")
    is_visible: bool = Field(default=True, description="Видимость анкеты (True/False)")
    is_verified: bool = Field(default=False, description="Отметка о верификации фото")
    has_medical_certificate: bool = Field(default=False, description="Отметка о наличии мед. справки")
    photos: list[str] = Field(default_factory=list, description="Список прямых URL-ссылок на фото (например: https://photos.domain.com/c/...)")



class UpdateFormRequest(ApiSchema):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    age: int | None = Field(default=None, ge=18, le=99)
    height: int | None = Field(default=None, ge=140, le=220)
    bust_size: int | None = Field(default=None, ge=0, le=10)
    caption: str | None = None
    one_hour_price: int | None = None
    two_hour_price: int | None = None
    three_hour_price: int | None = None
    overnight_price: int | None = None
    city_slot: int | None = Field(default=None, ge=1, le=2)
    sort_order: int | None = Field(default=None, ge=0)
    is_visible: bool | None = None
    is_verified: bool | None = None
    has_medical_certificate: bool | None = None
    rating: float | None = None
    orders: int | None = None
    public_channel_url: str | None = None


class SwapPositionsRequest(ApiSchema):
    code_a: str
    code_b: str


class ToggleFieldRequest(ApiSchema):
    field: str = Field(pattern="^(is_visible|is_verified|has_medical_certificate)$")


# ── Review schemas ────────────────────────────────────────────────────────


class ReviewItem(ApiSchema):
    id: int
    form_code: str
    author: str | None = None
    review_date: str | None = None
    body: str | None = None
    score: int = 0
    created_at: datetime


class ReviewsListResponse(ApiSchema):
    items: list[ReviewItem] = Field(default_factory=list)


class CreateReviewRequest(ApiSchema):
    author: str | None = Field(default=None, max_length=100)
    review_date: str | None = Field(default=None, max_length=50)
    body: str | None = Field(default=None, max_length=1000)
    score: int = Field(default=5, ge=1, le=5)


class UpdateReviewRequest(ApiSchema):
    author: str | None = None
    review_date: str | None = None
    body: str | None = None
    score: int | None = Field(default=None, ge=1, le=5)


# ── Service schemas ───────────────────────────────────────────────────────


class ServiceItem(ApiSchema):
    id: int
    form_code: str
    name: str
    created_at: datetime


class ServicesListResponse(ApiSchema):
    items: list[ServiceItem] = Field(default_factory=list)


class CreateServiceRequest(ApiSchema):
    name: str = Field(min_length=1, max_length=100)


class UpdateServiceRequest(ApiSchema):
    name: str = Field(min_length=1, max_length=100)


# ── Additional schemas ────────────────────────────────────────────────────


class AdditionalItem(ApiSchema):
    id: int
    form_code: str
    name: str
    price: int
    created_at: datetime


class AdditionalsListResponse(ApiSchema):
    items: list[AdditionalItem] = Field(default_factory=list)


class CreateAdditionalRequest(ApiSchema):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(ge=0)


class UpdateAdditionalRequest(ApiSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: int | None = Field(default=None, ge=0)


# ── Promo schemas ─────────────────────────────────────────────────────────


class PromoItem(ApiSchema):
    name: str
    discount: int
    created_at: datetime


class PromosListResponse(ApiSchema):
    items: list[PromoItem] = Field(default_factory=list)


class CreatePromoRequest(ApiSchema):
    name: str = Field(min_length=1, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    discount: int = Field(ge=0, le=100)
