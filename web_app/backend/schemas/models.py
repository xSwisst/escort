from __future__ import annotations

from pydantic import BaseModel, Field


class ModelPrices(BaseModel):
    one_hour: int | None = Field(None, alias="oneHour")
    two_hours: int | None = Field(None, alias="twoHours")
    three_hours: int | None = Field(None, alias="threeHours")
    night: int | None = None

    class Config:
        populate_by_name = True
        by_alias = True


class ModelFlags(BaseModel):
    verification: bool = False
    document: bool = False
    dynamic: bool = False

    class Config:
        populate_by_name = True
        by_alias = True


class ModelSummary(BaseModel):
    code: str
    name: str
    city_status: int = Field(1, alias="cityStatus")
    age: int = 0
    height: int = 0
    tits: int = 0
    description: str | None = None
    prices: ModelPrices = Field(default_factory=ModelPrices)
    flags: ModelFlags = Field(default_factory=ModelFlags)
    photo_refs: list[str] = Field(default_factory=list, alias="photoRefs")
    photo_urls: list[str] = Field(default_factory=list, alias="photoUrls")
    preview_photo_ref: str | None = Field(None, alias="previewPhotoRef")
    preview_photo_url: str | None = Field(None, alias="previewPhotoUrl")
    orders: int = 0
    rating: float = 0.0
    reviews_count: int = Field(0, alias="reviewsCount")
    is_favorite: bool = Field(False, alias="isFavorite")

    class Config:
        populate_by_name = True
        by_alias = True


class ModelListResponse(BaseModel):
    items: list[ModelSummary] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        by_alias = True


class ModelReviewItem(BaseModel):
    id: int = 0
    author: str | None = None
    review_date: str | None = Field(None, alias="reviewDate")
    body: str | None = None
    score: int = 0

    class Config:
        populate_by_name = True
        by_alias = True


class ModelServiceItem(BaseModel):
    id: int = 0
    name: str

    class Config:
        populate_by_name = True
        by_alias = True


class ModelAdditionalItem(BaseModel):
    id: int = 0
    name: str
    price: int = 0

    class Config:
        populate_by_name = True
        by_alias = True


class ModelDetailsResponse(ModelSummary):
    services: list[ModelServiceItem] = Field(default_factory=list)
    additionals: list[ModelAdditionalItem] = Field(default_factory=list)
    reviews: list[ModelReviewItem] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        by_alias = True


class FavoriteCodesResponse(BaseModel):
    codes: list[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        by_alias = True
