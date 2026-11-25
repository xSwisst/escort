from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.cities import City, ClientCity
from repository.repositories.base import BaseRepository


class CityRepository(BaseRepository[City]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, City)

    async def get_by_id(self, city_id: int) -> City | None:
        result = await self._session.execute(select(City).where(City.id == city_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> City | None:
        clean = (name or "").strip()
        if not clean:
            return None
        result = await self._session.execute(select(City).where(func.lower(City.name) == func.lower(clean)))
        return result.scalar_one_or_none()


class ClientCityRepository(BaseRepository[ClientCity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ClientCity)

    async def get_by_client(self, client_id: int) -> list[ClientCity]:
        result = await self._session.execute(
            select(ClientCity)
            .where(ClientCity.client_id == client_id)
            .order_by(ClientCity.slot.asc())
        )
        return list(result.scalars().all())

    async def get_by_slot(self, client_id: int, slot: int) -> ClientCity | None:
        result = await self._session.execute(
            select(ClientCity).where(ClientCity.client_id == client_id, ClientCity.slot == slot)
        )
        return result.scalar_one_or_none()

    async def get_active(self, client_id: int) -> ClientCity | None:
        result = await self._session.execute(
            select(ClientCity).where(ClientCity.client_id == client_id, ClientCity.is_active.is_(True))
        )
        active = result.scalar_one_or_none()
        if active is not None:
            return active
        return await self.get_by_slot(client_id, 1)

    async def set_city(
        self,
        client_id: int,
        city_name: str,
        *,
        slot: int = 1,
        city_id: int | None = None,
        activate: bool = True,
    ) -> ClientCity:
        if activate:
            await self._session.execute(
                update(ClientCity).where(ClientCity.client_id == client_id).values(is_active=False)
            )
        existing = await self.get_by_slot(client_id, slot)
        if existing is not None:
            existing.city_name = city_name
            existing.city_id = city_id
            if activate:
                existing.is_active = True
            await self._session.flush()
            await self._session.refresh(existing)
            return existing

        return await self.create(
            client_id=client_id,
            city_id=city_id,
            city_name=city_name,
            slot=slot,
            is_active=activate,
        )

    async def switch_slot(self, client_id: int, slot: int) -> ClientCity | None:
        target = await self.get_by_slot(client_id, slot)
        if target is None:
            return None
        await self._session.execute(
            update(ClientCity).where(ClientCity.client_id == client_id).values(is_active=False)
        )
        target.is_active = True
        await self._session.flush()
        await self._session.refresh(target)
        return target
