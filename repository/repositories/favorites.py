from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from repository.models.forms import FormFavorite
from repository.repositories.base import BaseRepository


class FavoriteRepository(BaseRepository[FormFavorite]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FormFavorite)

    async def get_by_user(self, user_id: int, *, include_form: bool = False) -> list[FormFavorite]:
        """
        Get all favorites for a user.

        Args:
            user_id: User ID
            include_form: Eager load the associated Form

        Returns:
            List of FormFavorite instances
        """
        stmt = (
            select(FormFavorite)
            .where(FormFavorite.user_id == user_id)
            .order_by(FormFavorite.created_at.desc(), FormFavorite.id.desc())
        )

        if include_form:
            stmt = stmt.options(
                selectinload(FormFavorite.form).selectinload(Form.profile),
                selectinload(FormFavorite.form).selectinload(Form.pricing),
                selectinload(FormFavorite.form).selectinload(Form.photos),
                selectinload(FormFavorite.form).selectinload(Form.publication),
            )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_paginated(
        self,
        user_id: int,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[FormFavorite], int]:
        from repository.models.forms import Form, FormProfile
        from sqlalchemy import func, or_

        stmt = (
            select(FormFavorite)
            .join(Form, FormFavorite.form_code == Form.code)
            .where(FormFavorite.user_id == user_id)
        )
        count_stmt = (
            select(func.count())
            .select_from(FormFavorite)
            .join(Form, FormFavorite.form_code == Form.code)
            .where(FormFavorite.user_id == user_id)
        )

        normalized_query = (query or "").strip()
        if normalized_query:
            pattern = f"%{normalized_query.lower()}%"
            stmt = stmt.outerjoin(FormProfile, Form.code == FormProfile.form_code)
            count_stmt = count_stmt.outerjoin(FormProfile, Form.code == FormProfile.form_code)
            filters = or_(
                FormFavorite.form_code.ilike(pattern),
                FormProfile.name.ilike(pattern),
            )
            if normalized_query.isdigit():
                filters = or_(filters, Form.id == int(normalized_query))
            stmt = stmt.where(filters)
            count_stmt = count_stmt.where(filters)

        total = int((await self._session.execute(count_stmt)).scalar_one())

        stmt = (
            stmt.options(
                selectinload(FormFavorite.form).selectinload(Form.profile),
                selectinload(FormFavorite.form).selectinload(Form.pricing),
                selectinload(FormFavorite.form).selectinload(Form.photos),
                selectinload(FormFavorite.form).selectinload(Form.publication),
            )
            .order_by(FormFavorite.created_at.desc(), FormFavorite.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        items = list((await self._session.execute(stmt)).scalars().all())
        return items, total

    async def toggle(self, user_id: int, form_code: str) -> bool:
        rows = await self._session.execute(select(FormFavorite).where(FormFavorite.user_id == user_id, FormFavorite.form_code == form_code))
        matches = list(rows.scalars().all())
        if matches:
            for row in matches:
                await self.delete_by_pk(row.id)
            return False
        await self.create(user_id=user_id, form_code=form_code)
        return True
