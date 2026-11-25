from __future__ import annotations
from typing import Any

from services.clients.service import ClientService
from services.orders.service import OrderService
from services.payments import PaymentService
from shared.bot.session import resolve_session
from .exceptions import ApiNotFoundError
from .schemas import (
    ClientCityItem,
    FavoriteItem,
    FavoritesResponse,
    OrderItem,
    OrdersResponse,
    ProfileResponse,
    PromoActivateResponse,
    TransactionItem,
    TransactionsResponse,
)


class ProfileApi:
    async def get_profile(self, user_id: int) -> ProfileResponse:
        async with resolve_session() as session:
            service = ClientService(session)
            p = await service.get_profile(user_id)
            return ProfileResponse(
                id=p.id,
                user_id=p.user_id,
                primary_city=p.primary_city,
                secondary_city=p.secondary_city,
                active_city_slot=p.active_city_slot,
                city=p.city,
                cities=[
                    ClientCityItem(slot=c.slot, city_name=c.city_name, is_active=c.is_active)
                    for c in (p.cities or [])
                ],
                rating=p.rating,
                orders=p.orders,
                balance=p.balance,
                promo=p.promo,
                registered_at=p.registered_at,
            )

    async def get_orders(
        self,
        user_id: int,
        *,
        query: str | None = None,
        status_filter: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> OrdersResponse:
        async with resolve_session() as session:
            service = OrderService(session)
            status_val = "pending" if status_filter == "active" else (
                status_filter if status_filter in {"completed", "rejected"} else None
            )
            orders, total = await service.get_orders_paginated(
                user_id=user_id,
                query=query,
                page=page,
                per_page=per_page,
                status=status_val,
            )
            items = []
            for o in orders:
                addr_text = None
                if getattr(o, "address", None):
                    addr_text = f"{o.address.title}: {o.address.address}" if o.address.title else o.address.address
                items.append(
                    OrderItem(
                        id=o.id,
                        order_number=str(o.id),
                        form_snapshot=o.form_snapshot,
                        city_name=o.city_name,
                        tariff_name=o.tariff_name,
                        status=o.status.value if hasattr(o.status, "value") else str(o.status),
                        created_at=o.created_at,
                        scheduled_month=o.scheduled_month,
                        scheduled_day=o.scheduled_day,
                        scheduled_time=o.scheduled_time,
                        meeting_place_type=o.meeting_place_type,
                        address_text=addr_text,
                    )
                )
            return OrdersResponse(items=items, total=total, page=page, per_page=per_page)

    async def get_order(self, user_id: int, order_number: str) -> OrderItem:
        async with resolve_session() as session:
            service = OrderService(session)
            o = await service.get_order_by_number(order_number)
            if not o or o.user_id != user_id:
                raise ApiNotFoundError(f"Order not found: {order_number}")
            addr_text = None
            if getattr(o, "address", None):
                addr_text = f"{o.address.title}: {o.address.address}" if o.address.title else o.address.address
            return OrderItem(
                id=o.id,
                order_number=str(o.id),
                form_snapshot=o.form_snapshot,
                city_name=o.city_name,
                tariff_name=o.tariff_name,
                status=o.status.value if hasattr(o.status, "value") else str(o.status),
                created_at=o.created_at,
                scheduled_month=o.scheduled_month,
                scheduled_day=o.scheduled_day,
                scheduled_time=o.scheduled_time,
                meeting_place_type=o.meeting_place_type,
                address_text=addr_text,
            )

    async def get_transactions(
        self,
        user_id: int,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> TransactionsResponse:
        async with resolve_session() as session:
            service = PaymentService(session)
            txs, total = await service.get_transactions_paginated(
                user_id=user_id,
                query=query,
                page=page,
                per_page=per_page,
            )
            items = [
                TransactionItem(
                    id=t.id,
                    user_id=t.user_id,
                    invoice_id=t.invoice_id,
                    type=t.type.value if hasattr(t.type, "value") else str(t.type),
                    amount=t.amount,
                    balance_after=t.balance_after,
                    purpose=t.purpose,
                    order_number=t.order_number,
                    description=t.description,
                    created_at=t.created_at,
                )
                for t in txs
            ]
            return TransactionsResponse(items=items, total=total, page=page, per_page=per_page)

    async def get_transaction(self, user_id: int, transaction_id: int) -> TransactionItem:
        async with resolve_session() as session:
            service = PaymentService(session)
            t = await service.get_transaction_by_id(transaction_id)
            if not t or t.user_id != user_id:
                raise ApiNotFoundError(f"Transaction not found: {transaction_id}")
            return TransactionItem(
                id=t.id,
                user_id=t.user_id,
                invoice_id=t.invoice_id,
                type=t.type.value if hasattr(t.type, "value") else str(t.type),
                amount=t.amount,
                balance_after=t.balance_after,
                purpose=t.purpose,
                order_number=t.order_number,
                description=t.description,
                created_at=t.created_at,
            )

    async def get_favorites(
        self,
        user_id: int,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> FavoritesResponse:
        async with resolve_session() as session:
            service = ClientService(session)
            favs, total = await service.get_favorites(user_id, query=query, page=page, per_page=per_page)
            items = []
            for fav in favs:
                f = fav.form
                if not f:
                    continue
                prof = f.profile
                pricing = f.pricing
                pub = f.publication
                photos = [str(p.storage_key).strip() for p in getattr(f, "photos", []) if str(p.storage_key).strip()]
                items.append(
                    FavoriteItem(
                        form_id=f.id,
                        form_code=f.code,
                        name=prof.name if prof else f.code,
                        age=int(prof.age or 0) if prof else 0,
                        height=int(prof.height or 0) if prof else 0,
                        bust_size=int(prof.bust_size or 0) if prof else 0,
                        price_1h=pricing.one_hour_price if pricing else None,
                        city_slot=pub.city_slot if pub else 1,
                        photo_url=photos[0] if photos else None,
                        photos=photos,
                    )
                )
            return FavoritesResponse(items=items, total=total, page=page, per_page=per_page)

    async def activate_promo(self, user_id: int, code: str) -> PromoActivateResponse:
        async with resolve_session() as session:
            service = ClientService(session)
            applied, promo_code = await service.activate_promo(user_id, code)
            return PromoActivateResponse(applied=applied, promo_code=promo_code)
