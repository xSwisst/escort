from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileAddressItem(BaseModel):
    id: int
    title: str
    address: str
    created_at: str | None = Field(None, alias="createdAt")

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileUserResponse(BaseModel):
    telegram_id: int = Field(..., alias="telegramId")
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    username: str | None = None
    photo_url: str | None = Field(None, alias="photoUrl")
    is_mock: bool = Field(False, alias="isMock")

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileClientResponse(BaseModel):
    worker_id: int | None = Field(None, alias="workerId")
    agreement_accepted: bool = Field(..., alias="agreementAccepted")
    agreement_id: str | None = Field(None, alias="agreementId")
    is_banned: bool = Field(False, alias="isBanned")
    city_status: int = Field(1, alias="cityStatus")
    first_city: str | None = Field(None, alias="firstCity")
    second_city: str | None = Field(None, alias="secondCity")
    orders: int = 0
    rating: float = 0.0
    promo: str | None = None
    promo_amount: int | None = Field(None, alias="promoAmount")
    date_register: str | None = Field(None, alias="dateRegister")
    address_system_enabled: bool = Field(True, alias="addressSystemEnabled")
    balance: int = 0

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileResponse(BaseModel):
    user: ProfileUserResponse
    client: ProfileClientResponse
    addresses: list[ProfileAddressItem] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileCityResponse(BaseModel):
    client: ProfileClientResponse

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileAddressResponse(BaseModel):
    addresses: list[ProfileAddressItem] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileCityUpdateRequest(BaseModel):
    cityName: str
    slot: int = 1


class ProfileCityStatusUpdateRequest(BaseModel):
    cityStatus: int


class ProfileAddressCreateRequest(BaseModel):
    title: str
    address: str


class ProfilePromo(BaseModel):
    code: str | None = None
    amount: int | None = None
    is_active: bool = Field(False, alias="isActive")

    class Config:
        populate_by_name = True
        by_alias = True


class ProfilePromoResponse(BaseModel):
    promo: ProfilePromo
    client: ProfileClientResponse | None = None

    class Config:
        populate_by_name = True
        by_alias = True


class ProfilePromoActivateRequest(BaseModel):
    code: str


class ProfileOrderHistoryItem(BaseModel):
    number: str
    date: str | None = None
    model_info: str | None = Field(None, alias="modelInfo")
    city: str | None = None
    status: str = "pending"
    tariff_plan: str | None = Field(None, alias="tariffPlan")
    promo: str | None = None

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileOrdersPagination(BaseModel):
    page: int = 1
    page_size: int = Field(100, alias="pageSize")
    total: int = 0
    total_pages: int = Field(1, alias="totalPages")

    class Config:
        populate_by_name = True
        by_alias = True


class ProfileOrdersResponse(BaseModel):
    items: list[ProfileOrderHistoryItem] = Field(default_factory=list)
    pagination: ProfileOrdersPagination = Field(default_factory=ProfileOrdersPagination)

    class Config:
        populate_by_name = True
        by_alias = True
