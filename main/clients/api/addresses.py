from __future__ import annotations

from .base import ApiSection
from .schemas import ActionStatusResponse, AddressItem, AddressListResponse


class AddressesApi(ApiSection):
    async def list(self, user_id: int) -> AddressListResponse:
        return await self._get(f"/client/v1/addresses/{user_id}", model=AddressListResponse)

    async def get(self, *, user_id: int, address_id: int) -> AddressItem:
        return await self._get(f"/client/v1/addresses/{user_id}/{address_id}", model=AddressItem)

    async def create(self, *, user_id: int, title: str, address: str) -> AddressItem:
        return await self._post(
            f"/client/v1/addresses/{user_id}",
            model=AddressItem,
            json={"title": title, "address": address},
        )

    async def update_title(self, *, user_id: int, address_id: int, title: str) -> AddressItem:
        return await self._patch(
            f"/client/v1/addresses/{user_id}/{address_id}/title",
            model=AddressItem,
            json={"title": title},
        )

    async def update_address(self, *, user_id: int, address_id: int, address: str) -> AddressItem:
        return await self._patch(
            f"/client/v1/addresses/{user_id}/{address_id}/address",
            model=AddressItem,
            json={"address": address},
        )

    async def delete(self, *, user_id: int, address_id: int) -> None:
        await self._delete(f"/client/v1/addresses/{user_id}/{address_id}", model=ActionStatusResponse)
