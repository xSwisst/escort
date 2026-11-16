from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.addresses import Address
from repositories.base import BaseRepository


class AddressRepository(BaseRepository[Address]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Address)

    async def get_by_user(self, user_id: int):
        result = await self._session.execute(
            select(Address).where(Address.user_id == user_id).order_by(Address.created_at.desc())
        )
        return result.scalars().all()
