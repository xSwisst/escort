from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from repository.repositories.addresses import AddressRepository
from repository.repositories.agreements import AgreementRepository
from repository.repositories.clients import ClientRepository
from repository.repositories.favorites import FavoriteRepository
from repository.repositories.orders import OrderRepository
from repository.repositories.promos import PromoRepository


@dataclass
class ClientProfile:
    id: int
    user_id: int
    primary_city: str | None
    secondary_city: str | None
    active_city_slot: int
    city: str | None
    rating: float
    orders: int
    balance: int
    promo: str | None
    promo_code: str | None
    registered_at: datetime


@dataclass
class BootstrapResult:
    client: Any
    agreement_required: bool
    agreement: Any | None


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.clients = ClientRepository(session)
        self.agreements = AgreementRepository(session)
        self.orders = OrderRepository(session)
        self.promos = PromoRepository(session)
        self.addresses = AddressRepository(session)
        self.favorites = FavoriteRepository(session)

    async def get_or_create_client(
        self,
        user_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ):
        return await self.clients.get_or_create(
            user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

    async def get_client(self, user_id: int):
        return await self.clients.get(user_id)

    async def get_client_by_db_id(self, db_id: int):
        return await self.clients.get_by_db_id(db_id)

    async def bootstrap(
        self,
        user_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ) -> BootstrapResult:
        client, _ = await self.get_or_create_client(
            user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        agreement = await self.get_active_agreement(user_id) if not client.has_accepted_agreement else None
        return BootstrapResult(
            client=client,
            agreement_required=not client.has_accepted_agreement,
            agreement=agreement,
        )

    async def accept_agreement(self, user_id: int, agreement_id: str | None = None) -> None:
        if not agreement_id:
            agreement = await self.get_active_agreement(user_id)
            agreement_id = getattr(agreement, "agreement_id", None) or "default"
        await self.set_agreement(user_id, agreement_id)

    async def set_agreement(self, user_id: int, agreement_id: str) -> None:
        await self.clients.set_agreement(user_id, agreement_id)

    async def get_active_agreement(self, user_id: int):
        client = await self.clients.get(user_id)
        agreement = await self.agreements.get(client.agreement_id) if client and client.agreement_id else None
        if agreement is not None:
            return agreement
        agreements = await self.agreements.get_all()
        return agreements[0] if agreements else None

    async def get_profile(self, user_id: int) -> ClientProfile:
        client, _ = await self.get_or_create_client(user_id)
        orders_count = await self.get_orders_count(user_id)
        active_slot = int(getattr(client, "active_city_slot", 1) or 1)
        active_city = client.secondary_city if active_slot == 2 and client.secondary_city else client.primary_city
        return ClientProfile(
            id=client.id,
            user_id=client.user_id,
            primary_city=client.primary_city,
            secondary_city=client.secondary_city,
            active_city_slot=active_slot,
            city=active_city,
            rating=float(client.rating or 0.0),
            orders=orders_count,
            balance=int(getattr(client, "balance", 0) or 0),
            promo=client.promo_code,
            promo_code=client.promo_code,
            registered_at=client.registered_at,
        )

    async def set_city(self, user_id: int, city: str, slot: int = 1) -> None:
        await self.clients.set_city(user_id, city, slot)

    async def switch_city(self, user_id: int, active_city_slot: int):
        return await self.clients.update_by_user_id(user_id, active_city_slot=active_city_slot)

    async def set_promo(self, user_id: int, promo_code: str) -> None:
        await self.clients.update_by_user_id(user_id, promo_code=promo_code)

    async def activate_promo(self, user_id: int, code: str) -> tuple[bool, str | None]:
        clean_code = (code or "").strip()
        promo = await self.promos.get_by_code(clean_code)
        if not promo:
            return False, None
        await self.set_promo(user_id, promo.code)
        return True, promo.code

    async def get_discount_amount(self, user_id: int) -> int | None:
        client = await self.clients.get(user_id)
        if not client or not client.promo_code:
            return None
        promo = await self.promos.get_by_code(client.promo_code)
        return int(promo.discount_amount) if promo and promo.discount_amount is not None else None

    async def get_orders_count(self, user_id: int) -> int:
        return await self.orders.count_by_user(user_id)

    async def get_favorites(self, user_id: int, query: str | None = None, page: int = 1, per_page: int = 10):
        return await self.favorites.get_by_user_paginated(user_id, query=query, page=page, per_page=per_page)

    async def toggle_favorite(self, user_id: int, form_code: str) -> bool:
        return await self.favorites.toggle(user_id, form_code)
