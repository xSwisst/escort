from __future__ import annotations

from .base import ApiSection
from .schemas import ActionStatusResponse, ClientCities, StartBootstrapResponse


class ClientApi(ApiSection):
    async def bootstrap(
        self,
        *,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ) -> StartBootstrapResponse:
        return await self._post(
            "/client/v1/clients/bootstrap",
            model=StartBootstrapResponse,
            json={
                "user": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                }
            },
        )

    async def accept_agreement(self, user_id: int) -> None:
        await self._post(
            "/client/v1/clients/accept-agreement",
            model=ActionStatusResponse,
            json={"user_id": user_id},
        )

    async def get_cities(self, user_id: int) -> ClientCities:
        return await self._get(f"/client/v1/clients/{user_id}/cities", model=ClientCities)

    async def set_city(self, user_id: int, *, city: str, slot: int) -> ClientCities:
        return await self._post(
            f"/client/v1/clients/{user_id}/cities",
            model=ClientCities,
            json={"city": city, "slot": slot},
        )

    async def switch_city(self, user_id: int, *, active_city_slot: int) -> ClientCities:
        return await self._post(
            f"/client/v1/clients/{user_id}/cities/switch",
            model=ClientCities,
            json={"active_city_slot": active_city_slot},
        )
