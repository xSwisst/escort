from __future__ import annotations

from typing import Any
from pydantic import BaseModel
from .base import ApiSection


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    form_code: str | None = None
    form_snapshot: str | None = None
    city_name: str | None = None
    tariff_name: str | None = None


class OrdersApi(ApiSection):
    async def create_order(self, payload: dict[str, Any]) -> OrderResponse:
        return await self._post("/client/v1/orders", model=OrderResponse, json=payload)

    async def get_order(self, order_id: int) -> OrderResponse:
        return await self._get(f"/client/v1/orders/{order_id}", model=OrderResponse)

    async def pay_balance(self, order_id: int | str, *, user_id: int, amount: int) -> dict[str, Any]:
        return await self._post(
            f"/client/v1/orders/{order_id}/pay-balance",
            json={"user_id": user_id, "amount": amount},
        )
