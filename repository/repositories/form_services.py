from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.forms import FormService
from repository.repositories.base import BaseRepository


class FormServiceRepository(BaseRepository[FormService]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FormService)

    async def get_by_form(self, form_code: str) -> list[FormService]:
        result = await self._session.execute(
            select(FormService).where(FormService.form_code == form_code).order_by(FormService.created_at.desc(), FormService.id.desc())
        )
        return list(result.scalars().all())

    async def create_service(self, form_code: str, **fields) -> FormService:
        """Create a new service for a form"""
        return await self.create(form_code=form_code, **fields)

    async def update_service(self, service_id: int, **fields) -> FormService | None:
        """Update service by ID"""
        return await self.update_by_pk(service_id, **fields)

    async def delete_service(self, service_id: int) -> bool:
        """Delete service by ID"""
        return await self.delete_by_pk(service_id)
