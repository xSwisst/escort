from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.forms import FormAdditional
from repository.repositories.base import BaseRepository


class FormAdditionalRepository(BaseRepository[FormAdditional]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FormAdditional)

    async def get_by_form(self, form_code: str) -> list[FormAdditional]:
        result = await self._session.execute(
            select(FormAdditional).where(FormAdditional.form_code == form_code).order_by(FormAdditional.created_at.desc(), FormAdditional.id.desc())
        )
        return list(result.scalars().all())

    async def create_additional(self, form_code: str, **fields) -> FormAdditional:
        """Create a new additional service for a form"""
        return await self.create(form_code=form_code, **fields)

    async def update_additional(self, additional_id: int, **fields) -> FormAdditional | None:
        """Update additional service by ID"""
        return await self.update_by_pk(additional_id, **fields)

    async def delete_additional(self, additional_id: int) -> bool:
        """Delete additional service by ID"""
        return await self.delete_by_pk(additional_id)
