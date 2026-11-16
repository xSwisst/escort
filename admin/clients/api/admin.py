from __future__ import annotations

from typing import Any

from .base import ApiSection
from .schemas import (
    ActionStatusResponse,
    AdditionalItem,
    AdditionalsListResponse,
    AdminClientDetailResponse,
    AdminClientListResponse,
    AdminClientLogDetailResponse,
    AdminClientLogsResponse,
    AgreementItem,
    AgreementsResponse,
    BroadcastResponse,
    CardItem,
    CardsListResponse,
    FormDetailResponse,
    FormsListResponse,
    PromoItem,
    PromosListResponse,
    ReviewItem,
    ReviewsListResponse,
    ServiceItem,
    ServicesListResponse,
)


class AdminApi(ApiSection):
    # ── Clients ──────────────────────────────────────────────────────────────

    async def list_clients(self, *, query: str | None = None, page: int = 1, per_page: int = 10) -> AdminClientListResponse:
        params = {"page": page, "per_page": per_page}
        if query is not None:
            params["q"] = query
        return await self._get(
            "/admin/v1/clients",
            model=AdminClientListResponse,
            params=params,
        )

    async def get_client(self, user_id: int) -> AdminClientDetailResponse:
        return await self._get(f"/admin/v1/clients/{user_id}", model=AdminClientDetailResponse)

    async def get_client_by_db_id(self, db_id: int) -> AdminClientDetailResponse:
        return await self._get(f"/admin/v1/clients/by-db-id/{db_id}", model=AdminClientDetailResponse)

    async def set_ban(self, *, user_id: int, is_banned: bool) -> ActionStatusResponse:
        return await self._patch(
            f"/admin/v1/clients/{user_id}/ban",
            model=ActionStatusResponse,
            json={"is_banned": is_banned},
        )

    async def set_agreement(self, *, user_id: int, agreement_id: str) -> ActionStatusResponse:
        return await self._patch(
            f"/admin/v1/clients/{user_id}/agreement",
            model=ActionStatusResponse,
            json={"agreement_id": agreement_id},
        )

    async def send_message_to_client(self, *, user_id: int, text: str) -> ActionStatusResponse:
        return await self._post(
            f"/admin/v1/clients/{user_id}/send-message",
            model=ActionStatusResponse,
            json={"text": text},
        )

    async def list_client_logs(
        self,
        client_id: int | str,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> AdminClientLogsResponse:
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if query:
            params["q"] = query
        return await self._get(
            f"/admin/v1/clients/{client_id}/logs",
            model=AdminClientLogsResponse,
            params=params,
        )

    async def get_client_log(self, log_id: int) -> AdminClientLogDetailResponse:
        return await self._get(
            f"/admin/v1/client-logs/{log_id}",
            model=AdminClientLogDetailResponse,
        )

    async def start_broadcast(self, payload: dict[str, Any]) -> BroadcastResponse:
        return await self._post(
            "/admin/v1/clients/broadcast",
            model=BroadcastResponse,
            json=payload,
        )

    # ── Agreements ────────────────────────────────────────────────────────────

    async def list_agreements(self) -> AgreementsResponse:
        return await self._get("/admin/v1/agreements", model=AgreementsResponse)

    async def create_agreement(self, payload: dict[str, Any]) -> AgreementItem:
        return await self._post(
            "/admin/v1/agreements",
            model=AgreementItem,
            json=payload,
        )

    async def delete_agreement(self, agreement_id: str) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/agreements/{agreement_id}",
            model=ActionStatusResponse,
        )

    # ── Forms (Models) ────────────────────────────────────────────────────────

    async def list_forms(self, city_slot: int | None = None) -> FormsListResponse:
        params = {}
        if city_slot is not None:
            params["city_slot"] = city_slot
        return await self._get(
            "/admin/v1/forms",
            model=FormsListResponse,
            params=params,
        )

    async def get_form(self, code: str) -> FormDetailResponse:
        return await self._get(
            f"/admin/v1/forms/{code}",
            model=FormDetailResponse,
        )

    async def create_form(self, form_data: dict[str, Any], files: list[tuple] | None = None) -> FormDetailResponse:
        kwargs: dict[str, Any] = {"data": form_data}
        if files:
            kwargs["files"] = files
        return await self._post(
            "/admin/v1/forms",
            model=FormDetailResponse,
            **kwargs,
        )

    async def update_form(self, code: str, payload: dict[str, Any]) -> FormDetailResponse:
        return await self._put(
            f"/admin/v1/forms/{code}",
            model=FormDetailResponse,
            json=payload,
        )

    async def delete_form(self, code: str) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/forms/{code}",
            model=ActionStatusResponse,
        )

    async def toggle_form_field(self, code: str, field: str) -> ActionStatusResponse:
        return await self._post(
            f"/admin/v1/forms/{code}/toggle",
            model=ActionStatusResponse,
            json={"field": field},
        )

    async def swap_positions(self, code_a: str, code_b: str) -> ActionStatusResponse:
        return await self._post(
            "/admin/v1/forms/swap-positions",
            model=ActionStatusResponse,
            json={"code_a": code_a, "code_b": code_b},
        )

    async def add_form_photos(self, code: str, files: list[tuple]) -> ActionStatusResponse:
        return await self._post(
            f"/admin/v1/forms/{code}/photos",
            model=ActionStatusResponse,
            files=files,
        )

    async def delete_form_photo(self, code: str, index: int) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/forms/{code}/photos/{index}",
            model=ActionStatusResponse,
        )

    # ── Reviews ───────────────────────────────────────────────────────────────

    async def list_reviews(self, code: str) -> ReviewsListResponse:
        return await self._get(
            f"/admin/v1/reviews/forms/{code}",
            model=ReviewsListResponse,
        )

    async def create_review(self, code: str, payload: dict[str, Any]) -> ReviewItem:
        return await self._post(
            f"/admin/v1/reviews/forms/{code}",
            model=ReviewItem,
            json=payload,
        )

    async def update_review(self, review_id: int, payload: dict[str, Any]) -> ReviewItem:
        return await self._put(
            f"/admin/v1/reviews/{review_id}",
            model=ReviewItem,
            json=payload,
        )

    async def delete_review(self, review_id: int) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/reviews/{review_id}",
            model=ActionStatusResponse,
        )

    # ── Services ──────────────────────────────────────────────────────────────

    async def list_services(self, code: str) -> ServicesListResponse:
        return await self._get(
            f"/admin/v1/services/forms/{code}",
            model=ServicesListResponse,
        )

    async def create_service(self, code: str, payload: dict[str, Any]) -> ServiceItem:
        return await self._post(
            f"/admin/v1/services/forms/{code}",
            model=ServiceItem,
            json=payload,
        )

    async def update_service(self, service_id: int, payload: dict[str, Any]) -> ServiceItem:
        return await self._put(
            f"/admin/v1/services/{service_id}",
            model=ServiceItem,
            json=payload,
        )

    async def delete_service(self, service_id: int) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/services/{service_id}",
            model=ActionStatusResponse,
        )

    # ── Additionals ───────────────────────────────────────────────────────────

    async def list_additionals(self, code: str) -> AdditionalsListResponse:
        return await self._get(
            f"/admin/v1/additionals/forms/{code}",
            model=AdditionalsListResponse,
        )

    async def create_additional(self, code: str, payload: dict[str, Any]) -> AdditionalItem:
        return await self._post(
            f"/admin/v1/additionals/forms/{code}",
            model=AdditionalItem,
            json=payload,
        )

    async def update_additional(self, additional_id: int, payload: dict[str, Any]) -> AdditionalItem:
        return await self._put(
            f"/admin/v1/additionals/{additional_id}",
            model=AdditionalItem,
            json=payload,
        )

    async def delete_additional(self, additional_id: int) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/additionals/{additional_id}",
            model=ActionStatusResponse,
        )

    # ── Promos ────────────────────────────────────────────────────────────────

    async def list_promos(self) -> PromosListResponse:
        return await self._get(
            "/admin/v1/promos",
            model=PromosListResponse,
        )

    async def create_promo(self, payload: dict[str, Any]) -> PromoItem:
        return await self._post(
            "/admin/v1/promos",
            model=PromoItem,
            json=payload,
        )

    async def delete_promo(self, name: str) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/promos/{name}",
            model=ActionStatusResponse,
        )

    # ── Cards ─────────────────────────────────────────────────────────────────

    async def list_cards(self) -> CardsListResponse:
        return await self._get(
            "/admin/v1/cards",
            model=CardsListResponse,
        )

    async def create_card(self, payload: dict[str, Any]) -> CardItem:
        return await self._post(
            "/admin/v1/cards",
            model=CardItem,
            json=payload,
        )

    async def toggle_card(self, card_id: int) -> CardItem:
        return await self._post(
            f"/admin/v1/cards/{card_id}/toggle",
            model=CardItem,
        )

    async def delete_card(self, card_id: int) -> ActionStatusResponse:
        return await self._delete(
            f"/admin/v1/cards/{card_id}",
            model=ActionStatusResponse,
        )
