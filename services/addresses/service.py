from sqlalchemy.ext.asyncio import AsyncSession

from repository.repositories.addresses import AddressRepository
from repository.repositories.clients import ClientRepository


class AddressService:
    def __init__(self, session: AsyncSession) -> None:
        self.addresses = AddressRepository(session)
        self.clients = ClientRepository(session)

    async def list_user_addresses(self, user_id: int):
        return await self.addresses.get_by_user(user_id)

    async def get_address(self, address_id: int):
        return await self.addresses.get(address_id)

    async def create_address(self, user_id: int, *, title: str, address: str):
        return await self.addresses.create(user_id=user_id, label=title, full_address=address)

    async def update_address(self, address_id: int, **fields):
        return await self.addresses.update_by_pk(address_id, **fields)

    async def delete_address(self, address_id: int) -> bool:
        return await self.addresses.delete_by_pk(address_id)
