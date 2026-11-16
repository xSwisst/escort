from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.promos import Promo
from repositories.base import BaseRepository


class PromoRepository(BaseRepository[Promo]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Promo)

    async def get_by_code(self, code: str) -> Promo | None:
        """Get promo by code (case-insensitive)"""
        clean_code = (code or "").strip()
        if not clean_code:
            return None
        result = await self._session.execute(
            select(Promo).where(func.lower(Promo.code) == func.lower(clean_code))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Promo | None:
        """Get promo by name/code"""
        return await self.get_by_code(name)

    async def create_promo(self, **fields) -> Promo:
        """Create a new promo"""
        if "name" in fields and "code" not in fields:
            fields["code"] = fields.pop("name")
        if "discount" in fields and "discount_amount" not in fields:
            fields["discount_amount"] = fields.pop("discount")
        return await self.create(**fields)

    async def delete_by_name(self, name: str) -> bool:
        """Delete promo by name"""
        promo = await self.get_by_name(name)
        if not promo:
            return False
        await self._session.delete(promo)
        await self._session.flush()
        return True
