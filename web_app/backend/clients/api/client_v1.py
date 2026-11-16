from __future__ import annotations

from .base import ApiSection
from .schemas import (
    AddressItem,
    AddressListResponse,
    ClientCitiesResponse,
    FavoriteToggleResponse,
    FavoritesResponse,
    FormAdditionalsResponse,
    FormCardResponse,
    FormReviewsResponse,
    FormServicesResponse,
    FormsListResponse,
    OrdersResponse,
    ProfileResponse,
    PromoActivateResponse,
    StartBootstrapResponse,
    AgreementInfo,
)


class ClientV1Api(ApiSection):
    async def bootstrap_client_with_init_data(self, *, init_data: str) -> StartBootstrapResponse:
        return await self._post(
            "/client/v1/clients/bootstrap",
            model=StartBootstrapResponse,
            json={"init_data": init_data},
        )

    async def bootstrap_client(self, *, user_id: int, first_name: str | None, last_name: str | None, username: str | None) -> StartBootstrapResponse:
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

    async def accept_agreement(self, *, user_id: int) -> None:
        await self._post("/client/v1/clients/accept-agreement", model=AgreementInfo, json={"user_id": user_id})

    async def get_cities(self, *, user_id: int) -> ClientCitiesResponse:
        return await self._get(f"/client/v1/clients/{user_id}/cities", model=ClientCitiesResponse)

    async def set_city(self, *, user_id: int, city: str, slot: int = 1) -> ClientCitiesResponse:
        return await self._post(
            f"/client/v1/clients/{user_id}/cities",
            model=ClientCitiesResponse,
            json={"city": city, "slot": slot},
        )

    async def switch_city(self, *, user_id: int, active_city_slot: int) -> ClientCitiesResponse:
        return await self._post(
            f"/client/v1/clients/{user_id}/cities/switch",
            model=ClientCitiesResponse,
            json={"active_city_slot": active_city_slot},
        )

    async def get_agreement(self, *, user_id: int) -> AgreementInfo:
        return await self._get("/client/v1/info/agreement", model=AgreementInfo, params={"user_id": user_id})

    async def get_profile(self, *, user_id: int) -> ProfileResponse:
        return await self._get("/client/v1/profile", model=ProfileResponse, params={"user_id": user_id})

    async def get_orders(self, *, user_id: int, status_filter: str = "all") -> OrdersResponse:
        return await self._get(
            "/client/v1/profile/orders",
            model=OrdersResponse,
            params={"user_id": user_id, "status_filter": status_filter},
        )

    async def get_favorites(self, *, user_id: int) -> FavoritesResponse:
        return await self._get("/client/v1/profile/favorites", model=FavoritesResponse, params={"user_id": user_id})

    async def activate_promo(self, *, user_id: int, code: str) -> PromoActivateResponse:
        return await self._post("/client/v1/profile/promo", model=PromoActivateResponse, params={"user_id": user_id}, json={"code": code})

    async def list_forms(self, *, user_id: int, active_city_slot: int | None = None) -> FormsListResponse:
        params = {"user_id": user_id}
        if active_city_slot is not None:
            params["active_city_slot"] = active_city_slot
        return await self._get("/client/v1/forms", model=FormsListResponse, params=params)

    async def get_form_card(self, *, user_id: int, form_code: str) -> FormCardResponse:
        return await self._get(f"/client/v1/forms/{form_code}/card", model=FormCardResponse, params={"user_id": user_id})

    async def toggle_favorite(self, *, user_id: int, form_code: str) -> FavoriteToggleResponse:
        return await self._post(f"/client/v1/forms/{form_code}/favorite", model=FavoriteToggleResponse, params={"user_id": user_id})

    async def get_reviews(self, *, form_code: str) -> FormReviewsResponse:
        return await self._get(f"/client/v1/forms/{form_code}/reviews", model=FormReviewsResponse)

    async def get_services(self, *, form_code: str) -> FormServicesResponse:
        return await self._get(f"/client/v1/forms/{form_code}/services", model=FormServicesResponse)

    async def get_additionals(self, *, form_code: str) -> FormAdditionalsResponse:
        return await self._get(f"/client/v1/forms/{form_code}/additionals", model=FormAdditionalsResponse)

    async def list_addresses(self, *, user_id: int) -> AddressListResponse:
        return await self._get(f"/client/v1/addresses/{user_id}", model=AddressListResponse)

    async def create_address(self, *, user_id: int, title: str, address: str) -> AddressItem:
        return await self._post(f"/client/v1/addresses/{user_id}", model=AddressItem, json={"title": title, "address": address})

    async def delete_address(self, *, user_id: int, address_id: int) -> None:
        await self._client.delete(f"/client/v1/addresses/{user_id}/{address_id}")
