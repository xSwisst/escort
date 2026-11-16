from sqlalchemy.ext.asyncio import AsyncSession

from repositories.addresses import AddressRepository
from repositories.agreements import AgreementRepository
from repositories.clients import ClientRepository
from repositories.favorites import FavoriteRepository
from repositories.orders import OrderRepository
from repositories.promos import PromoRepository


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.clients = ClientRepository(session)
        self.agreements = AgreementRepository(session)
        self.orders = OrderRepository(session)
        self.promos = PromoRepository(session)
        self.addresses = AddressRepository(session)
        self.favorites = FavoriteRepository(session)

    async def get_or_create_client(self, user_id: int, *, first_name: str | None = None, last_name: str | None = None, username: str | None = None):
        return await self.clients.get_or_create(user_id, first_name=first_name, last_name=last_name, username=username)

    async def get_client(self, user_id: int):
        return await self.clients.get(user_id)

    async def get_client_by_db_id(self, db_id: int):
        return await self.clients.get_by_db_id(db_id)

    async def set_agreement(self, user_id: int, agreement_id: str) -> None:
        await self.clients.set_agreement(user_id, agreement_id)

    async def get_active_agreement(self, user_id: int):
        client = await self.clients.get(user_id)
        agreement = await self.agreements.get(client.agreement_id) if client and client.agreement_id else None
        if agreement is not None:
            return agreement
        agreements = await self.agreements.get_all()
        return agreements[0] if agreements else None

    async def set_city(self, user_id: int, city: str, slot: int = 1) -> None:
        await self.clients.set_city(user_id, city, slot)

    async def set_promo(self, user_id: int, promo_code: str) -> None:
        await self.clients.update_by_user_id(user_id, promo_code=promo_code)

    async def get_discount_amount(self, user_id: int) -> int | None:
        client = await self.clients.get(user_id)
        if not client or not client.promo_code:
            return None
        promo = await self.promos.get_by(code=client.promo_code)
        return int(promo.discount_amount) if promo and promo.discount_amount is not None else None

    async def get_orders_count(self, user_id: int) -> int:
        return await self.orders.count_by_user(user_id)
