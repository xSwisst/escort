from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from repository.repositories.addresses import AddressRepository
from repository.repositories.clients import ClientRepository


class AddressService:
    def __init__(self, session: AsyncSession) -> None:
        self.addresses = AddressRepository(session)
        self.clients = ClientRepository(session)

    async def list_user_addresses(self, user_id: int):
        return await self.addresses.get_by_user(user_id)

    async def list(self, user_id: int):
        return await self.addresses.get_by_user(user_id)

    async def get(self, user_id: int, address_id: int):
        addr = await self.addresses.get(address_id)
        if addr and addr.user_id == user_id:
            return addr
        return None

    async def get_address(self, address_id: int):
        return await self.addresses.get(address_id)

    async def create_address(self, user_id: int, *, title: str, address: str):
        return await self.addresses.create(user_id=user_id, label=title, full_address=address)

    async def create(self, user_id: int, title: str, address: str):
        return await self.create_address(user_id, title=title, address=address)

    async def update_title(self, user_id: int, address_id: int, title: str):
        addr = await self.get(user_id, address_id)
        if addr:
            addr.label = title
            await self.addresses._session.flush()
        return addr

    async def update_address(self, address_id: int, **fields):
        return await self.addresses.update_by_pk(address_id, **fields)

    async def update_address_text(self, user_id: int, address_id: int, address: str):
        addr = await self.get(user_id, address_id)
        if addr:
            addr.full_address = address
            await self.addresses._session.flush()
        return addr

    async def delete_address(self, address_id: int) -> bool:
        return await self.addresses.delete_by_pk(address_id)

    async def delete(self, user_id: int, address_id: int) -> bool:
        addr = await self.get(user_id, address_id)
        if addr:
            await self.addresses._session.delete(addr)
            await self.addresses._session.flush()
            return True
        return False
