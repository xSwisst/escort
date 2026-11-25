from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.admins import Admin
from repository.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Admin)

    async def get_by_id(self, admin_id: int) -> Admin | None:
        result = await self._session.execute(select(Admin).where(Admin.id == admin_id))
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> Admin | None:
        result = await self._session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        *,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> tuple[Admin, bool]:
        existing = await self.get_by_telegram_id(telegram_id)
        if existing is not None:
            changed = False
            for field, val in (("username", username), ("first_name", first_name), ("last_name", last_name)):
                if val is not None and getattr(existing, field) != val:
                    setattr(existing, field, val)
                    changed = True
            if changed:
                await self._session.flush()
                await self._session.refresh(existing)
            return existing, False

        created = await self.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        return created, True
