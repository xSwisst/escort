from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.payments import Transaction, TransactionType
from repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Transaction)

    async def create_transaction(
        self,
        *,
        user_id: int,
        amount: int,
        type: TransactionType | str = TransactionType.ORDER_PAYMENT,
        status: str = "completed",
        description: str | None = None,
        invoice_id: int | None = None,
        order_number: str | int | None = None,
        balance_after: int | None = None,
    ) -> Transaction:
        if isinstance(type, str):
            try:
                type_val = TransactionType(type)
            except ValueError:
                type_val = TransactionType.ORDER_PAYMENT
        else:
            type_val = type

        tx = Transaction(
            user_id=user_id,
            amount=amount,
            type=type_val,
            status=status,
            description=description,
            invoice_id=invoice_id,
            order_number=str(order_number) if order_number is not None else None,
            balance_after=balance_after,
        )
        self._session.add(tx)
        await self._session.flush()
        return tx

    async def get_by_user_paginated(
        self,
        user_id: int,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[Transaction], int]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        count_stmt = select(func.count()).select_from(Transaction).where(Transaction.user_id == user_id)

        if query:
            q = f"%{query}%"
            filter_clause = or_(
                Transaction.description.ilike(q),
                Transaction.order_number.ilike(q),
            )
            stmt = stmt.where(filter_clause)
            count_stmt = count_stmt.where(filter_clause)

        total_res = await self._session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.order_by(Transaction.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        res = await self._session.execute(stmt)
        items = list(res.scalars().all())
        return items, total
