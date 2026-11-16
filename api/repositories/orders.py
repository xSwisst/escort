from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.orders import Order
from repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Order)

    async def get_by_user(
        self,
        user_id: int,
        status: str | None = None,
        *,
        include_form: bool = False,
        include_address: bool = False,
    ):
        """
        Get all orders for a user.

        Args:
            user_id: User ID
            status: Optional status filter
            include_form: Eager load the associated Form
            include_address: Eager load the associated Address

        Returns:
            List of Order instances
        """
        statement = select(Order).where(Order.user_id == user_id)

        if status:
            statement = statement.where(Order.status == status)

        if include_form:
            statement = statement.options(selectinload(Order.form))
        if include_address:
            statement = statement.options(selectinload(Order.address))

        statement = statement.order_by(Order.created_at.desc())
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def get_by_user_paginated(
        self,
        user_id: int,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
        status: str | None = None,
    ) -> tuple[list[Order], int]:
        stmt = select(Order).where(Order.user_id == user_id)
        count_stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)

        if status:
            stmt = stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)

        if query:
            q = f"%{query}%"
            filter_conditions = [
                Order.form_snapshot.ilike(q),
                Order.city_name.ilike(q),
                Order.tariff_name.ilike(q),
            ]
            if query.isdigit():
                filter_conditions.append(Order.id == int(query))
            filter_clause = or_(*filter_conditions)
            stmt = stmt.where(filter_clause)
            count_stmt = count_stmt.where(filter_clause)

        total_res = await self._session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.options(selectinload(Order.form), selectinload(Order.address))
        stmt = stmt.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        res = await self._session.execute(stmt)
        items = list(res.scalars().all())
        return items, total

    async def get_by_id(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.form), selectinload(Order.address))
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_order_number(self, order_number: str | int) -> Order | None:
        try:
            order_id = int(str(order_number).strip().lstrip("#"))
            return await self.get_by_id(order_id)
        except (ValueError, TypeError):
            return None

    async def count_by_user(self, user_id: int) -> int:
        return await self.count(user_id=user_id)

