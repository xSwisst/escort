from __future__ import annotations
from typing import Any

from .base import ApiSection
from .schemas import (
    FavoritesResponse,
    OrderItem,
    OrdersResponse,
    ProfileResponse,
    PromoActivateResponse,
    TransactionItem,
    TransactionsResponse,
)


class ProfileApi(ApiSection):
    async def get_profile(self, user_id: int) -> ProfileResponse:
        return await self._get("/client/v1/profile", model=ProfileResponse, params={"user_id": user_id})

    async def get_orders(
        self,
        *,
        user_id: int,
        query: str | None = None,
        status_filter: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> OrdersResponse:
        params: dict = {"user_id": user_id, "page": page, "per_page": per_page}
        if query:
            params["query"] = query
        if status_filter:
            params["status_filter"] = status_filter
        return await self._get(
            "/client/v1/profile/orders",
            model=OrdersResponse,
            params=params,
        )

    async def get_order(self, *, user_id: int, order_number: str) -> OrderItem:
        return await self._get(
            f"/client/v1/profile/orders/{order_number}",
            model=OrderItem,
            params={"user_id": user_id},
        )

    async def get_transactions(
        self,
        *,
        user_id: int,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> TransactionsResponse:
        params: dict = {"user_id": user_id, "page": page, "per_page": per_page}
        if query:
            params["query"] = query
        return await self._get(
            "/client/v1/profile/transactions",
            model=TransactionsResponse,
            params=params,
        )

    async def get_transaction(self, *, user_id: int, transaction_id: int) -> TransactionItem:
        return await self._get(
            f"/client/v1/profile/transactions/{transaction_id}",
            model=TransactionItem,
            params={"user_id": user_id},
        )

    async def get_favorites(
        self,
        user_id: int,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> FavoritesResponse:
        params: dict[str, Any] = {"user_id": user_id, "page": page, "per_page": per_page}
        if query is not None:
            params["q"] = query
        return await self._get("/client/v1/profile/favorites", model=FavoritesResponse, params=params)

    async def activate_promo(self, *, user_id: int, code: str) -> PromoActivateResponse:
        return await self._post(
            "/client/v1/profile/promo",
            model=PromoActivateResponse,
            params={"user_id": user_id},
            json={"code": code},
        )

