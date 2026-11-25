from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.promos import Promo
from repository.repositories.base import BaseRepository


class PromoRepository(BaseRepository[Promo]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Promo)

    async def list_by_admin(self, admin_id: int | None = None) -> list[Promo]:
        stmt = select(Promo).order_by(Promo.created_at.desc())
        if admin_id is not None:
            stmt = stmt.where(Promo.admin_id == admin_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, code: str, *, admin_id: int | None = None) -> Promo | None:
        """Get promo by code (case-insensitive)"""
        clean_code = (code or "").strip()
        if not clean_code:
            return None
        stmt = select(Promo).where(func.lower(Promo.code) == func.lower(clean_code))
        if admin_id is not None:
            stmt = stmt.where(Promo.admin_id == admin_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, *, admin_id: int | None = None) -> Promo | None:
        """Get promo by name/code"""
        return await self.get_by_code(name, admin_id=admin_id)

    async def create_promo(self, **fields) -> Promo:
        """Create a new promo"""
        if "name" in fields and "code" not in fields:
            fields["code"] = fields.pop("name")
        if "discount" in fields and "discount_amount" not in fields:
            fields["discount_amount"] = fields.pop("discount")
        return await self.create(**fields)

    async def delete_by_name(self, name: str, *, admin_id: int | None = None) -> bool:
        """Delete promo by name"""
        promo = await self.get_by_name(name, admin_id=admin_id)
        if not promo:
            return False
        await self._session.delete(promo)
        await self._session.flush()
        return True
