from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from repository.repositories.addresses import AddressRepository
from repository.repositories.admins import AdminRepository
from repository.repositories.agreements import AgreementRepository
from repository.repositories.cities import CityRepository, ClientCityRepository
from repository.repositories.clients import ClientRepository
from repository.repositories.favorites import FavoriteRepository
from repository.repositories.orders import OrderRepository
from repository.repositories.promos import PromoRepository


@dataclass
class ClientCityData:
    slot: int
    city_name: str
    city_id: int | None = None
    is_active: bool = False


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
    cities: list[ClientCityData] = field(default_factory=list)


@dataclass
class BootstrapResult:
    client: Any
    agreement_required: bool
    agreement: Any | None


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.admins = AdminRepository(session)
        self.cities = CityRepository(session)
        self.client_cities = ClientCityRepository(session)
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
        admin_id: int | None = None,
    ):
        valid_admin_id: int | None = None
        if admin_id is not None:
            admin = await self.admins.get_by_id(admin_id)
            if admin is not None:
                valid_admin_id = admin.id
        return await self.clients.get_or_create(
            user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            admin_id=valid_admin_id,
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
        admin_id: int | None = None,
    ) -> BootstrapResult:
        client, _ = await self.get_or_create_client(
            user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            admin_id=admin_id,
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
            agreement_id = getattr(agreement, "agreement_id", None) if agreement else None
        else:
            existing = await self.agreements.get(agreement_id)
            if not existing:
                agreement_id = None
        await self.set_agreement(user_id, agreement_id)

    async def set_agreement(self, user_id: int, agreement_id: str | None = None) -> None:
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
        links = await self.client_cities.get_by_client(user_id)
        if links:
            slot1 = next((c for c in links if c.slot == 1), None)
            slot2 = next((c for c in links if c.slot == 2), None)
            active_link = next((c for c in links if c.is_active), None) or slot1 or links[0]
            primary_city = slot1.city_name if slot1 else client.primary_city
            secondary_city = slot2.city_name if slot2 else client.secondary_city
            active_slot = active_link.slot
            active_city = active_link.city_name
            cities_list = [
                ClientCityData(
                    slot=c.slot,
                    city_name=c.city_name,
                    city_id=c.city_id,
                    is_active=bool(c.is_active),
                )
                for c in links
            ]
        else:
            active_slot = int(getattr(client, "active_city_slot", 1) or 1)
            primary_city = client.primary_city
            secondary_city = client.secondary_city
            active_city = secondary_city if active_slot == 2 and secondary_city else primary_city
            cities_list = []
            if primary_city:
                cities_list.append(ClientCityData(slot=1, city_name=primary_city, is_active=(active_slot == 1)))
            if secondary_city:
                cities_list.append(ClientCityData(slot=2, city_name=secondary_city, is_active=(active_slot == 2)))
        return ClientProfile(
            id=client.id,
            user_id=client.user_id,
            primary_city=primary_city,
            secondary_city=secondary_city,
            active_city_slot=active_slot,
            city=active_city,
            rating=float(client.rating or 0.0),
            orders=orders_count,
            balance=int(getattr(client, "balance", 0) or 0),
            promo=client.promo_code,
            promo_code=client.promo_code,
            registered_at=client.registered_at,
            cities=cities_list,
        )

    async def has_city(self, user_id: int, city: str) -> bool:
        target = (city or "").strip().lower()
        if not target:
            return False
        links = await self.client_cities.get_by_client(user_id)
        if links:
            return any((c.city_name or "").strip().lower() == target for c in links)
        client = await self.clients.get(user_id)
        if not client:
            return False
        return any(
            (val or "").strip().lower() == target
            for val in (client.primary_city, client.secondary_city)
            if val
        )

    async def set_city(self, user_id: int, city: str, slot: int | None = None) -> None:
        if await self.has_city(user_id, city):
            raise ValueError("duplicate_city")
        if slot is None:
            links = await self.client_cities.get_by_client(user_id)
            slot = (max((c.slot for c in links), default=0) + 1) if links else 1
        city_id: int | None = None
        if slot >= 2:
            city_obj = await self.cities.get_by_name(city)
            city_id = city_obj.id if city_obj is not None else None
        await self.client_cities.set_city(user_id, city, slot=slot, city_id=city_id, activate=True)
        await self.clients.set_city(user_id, city, slot)

    async def switch_city(self, user_id: int, active_city_slot: int):
        await self.client_cities.switch_slot(user_id, active_city_slot)
        return await self.clients.update_by_user_id(user_id, active_city_slot=active_city_slot)

    async def set_promo(self, user_id: int, promo_code: str) -> None:
        await self.clients.update_by_user_id(user_id, promo_code=promo_code)

    async def activate_promo(self, user_id: int, code: str) -> tuple[bool, str | None]:
        clean_code = (code or "").strip()
        client = await self.clients.get(user_id)
        if not client or client.admin_id is None:
            return False, None
        promo = await self.promos.get_by_code(clean_code, admin_id=client.admin_id)
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
