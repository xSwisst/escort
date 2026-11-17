from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.forms import FormReview
from repository.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[FormReview]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FormReview)

    async def get_by_form(self, form_code: str) -> list[FormReview]:
        result = await self._session.execute(
            select(FormReview).where(FormReview.form_code == form_code).order_by(FormReview.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_review(self, form_code: str, **fields) -> FormReview:
        """Create a new review for a form"""
        return await self.create(form_code=form_code, **fields)

    async def update_review(self, review_id: int, **fields) -> FormReview | None:
        """Update review by ID"""
        return await self.update_by_pk(review_id, **fields)

    async def delete_review(self, review_id: int) -> bool:
        """Delete review by ID"""
        return await self.delete_by_pk(review_id)
