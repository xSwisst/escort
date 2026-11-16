from __future__ import annotations

from .base import ApiSection
from .schemas import (
    FavoriteToggleResponse,
    FormAdditionalsResponse,
    FormCard,
    FormPrivateChannelResponse,
    FormReviewsResponse,
    FormServicesResponse,
    FormsListResponse,
)


class FormsApi(ApiSection):
    async def list_forms(self, *, user_id: int, active_city_slot: int | None = None) -> FormsListResponse:
        params = {"user_id": user_id}
        if active_city_slot is not None:
            params["active_city_slot"] = active_city_slot
        return await self._get("/client/v1/forms", model=FormsListResponse, params=params)

    async def get_form_card(self, *, user_id: int, form_code: str) -> FormCard:
        return await self._get(f"/client/v1/forms/{form_code}/card", model=FormCard, params={"user_id": user_id})

    async def toggle_favorite(self, *, user_id: int, form_code: str) -> FavoriteToggleResponse:
        return await self._post(
            f"/client/v1/forms/{form_code}/favorite",
            model=FavoriteToggleResponse,
            params={"user_id": user_id},
        )

    async def get_reviews(self, form_code: str) -> FormReviewsResponse:
        return await self._get(f"/client/v1/forms/{form_code}/reviews", model=FormReviewsResponse)

    async def get_additionals(self, form_code: str) -> FormAdditionalsResponse:
        return await self._get(f"/client/v1/forms/{form_code}/additionals", model=FormAdditionalsResponse)

    async def get_services(self, form_code: str) -> FormServicesResponse:
        return await self._get(f"/client/v1/forms/{form_code}/services", model=FormServicesResponse)

    async def get_private_channel(self, form_code: str) -> FormPrivateChannelResponse:
        return await self._get(f"/client/v1/forms/{form_code}/private-channel", model=FormPrivateChannelResponse)
