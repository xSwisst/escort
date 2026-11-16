from __future__ import annotations

from pydantic import BaseModel, Field

from .common import ApiSchema


class AddressItem(ApiSchema):
    id: int
    title: str
    address: str


class AddressListResponse(ApiSchema):
    items: list[AddressItem] = Field(default_factory=list)


class AddressCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    address: str = Field(min_length=1, max_length=1000)


class AddressUpdateTitleRequest(BaseModel):
    title: str = Field(min_length=1, max_length=256)


class AddressUpdateAddressRequest(BaseModel):
    address: str = Field(min_length=1, max_length=1000)
