from __future__ import annotations

from typing import Any
from pydantic import BaseModel

from services.clients.service import ClientService
from services.orders.service import OrderService
from services.payments import PaymentService
from shared.bot.session import resolve_session
from .exceptions import ApiClientError, ApiNotFoundError


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    form_code: str | None = None
    form_snapshot: str | None = None
    city_name: str | None = None
    tariff_name: str | None = None


class OrdersApi:
    async def create_order(self, payload: dict[str, Any]) -> OrderResponse:
        async with resolve_session() as session:
            os = OrderService(session)
            order = await os.orders.create(**payload)
            return OrderResponse(
                id=order.id,
                order_number=str(order.id),
                user_id=order.user_id,
                status=order.status.value if hasattr(order.status, "value") else str(order.status),
                form_code=order.form_code,
                form_snapshot=order.form_snapshot,
                city_name=order.city_name,
                tariff_name=order.tariff_name,
            )

    async def get_order(self, order_id: int) -> OrderResponse:
        async with resolve_session() as session:
            os = OrderService(session)
            order = await os.get_order_by_id(order_id)
            if not order:
                raise ApiNotFoundError(f"Order not found: {order_id}")
            return OrderResponse(
                id=order.id,
                order_number=str(order.id),
                user_id=order.user_id,
                status=order.status.value if hasattr(order.status, "value") else str(order.status),
                form_code=order.form_code,
                form_snapshot=order.form_snapshot,
                city_name=order.city_name,
                tariff_name=order.tariff_name,
            )

    async def pay_balance(self, order_id: int | str, *, user_id: int, amount: int) -> dict[str, Any]:
        async with resolve_session() as session:
            cs = ClientService(session)
            os = OrderService(session)
            ps = PaymentService(session)
            client = await cs.get_client(user_id)
            if not client or client.balance < amount:
                raise ApiClientError("Insufficient balance")
            client.balance -= amount
            clean_id = int(str(order_id).strip().lstrip("#"))
            order = await os.get_order_by_id(clean_id)
            if order:
                order.status = "completed"
            await ps.transactions.create_transaction(
                user_id=user_id,
                amount=amount,
                type="balance_payment",
                status="completed",
                order_number=str(order_id),
                balance_after=client.balance,
                description=f"Оплата заказа #{order_id} с баланса",
            )
            return {"ok": True, "balance": client.balance}
