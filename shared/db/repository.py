from __future__ import annotations

from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: Type[T]

    def __init__(self, session: AsyncSession, model: Type[T] | None = None) -> None:
        self._session = session
        if model is not None:
            self.model = model

    async def get(self, pk: Any) -> T | None:
        return await self._session.get(self.model, pk)

    async def get_by(self, **filters: Any) -> T | None:
        result = await self._session.execute(select(self.model).filter_by(**filters))
        return result.scalar_one_or_none()

    async def get_all(self, **filters: Any) -> Sequence[T]:
        statement = select(self.model).filter_by(**filters) if filters else select(self.model)
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def count(self, **filters: Any) -> int:
        statement = select(func.count()).select_from(self.model)
        if filters:
            statement = statement.filter_by(**filters)
        result = await self._session.execute(statement)
        return result.scalar_one()

    async def exists(self, **filters: Any) -> bool:
        return (await self.count(**filters)) > 0

    async def create(self, **fields: Any) -> T:
        obj = self.model(**fields)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update_by_pk(self, pk: Any, **fields: Any) -> T | None:
        obj = await self.get(pk)
        if obj is None:
            return None
        for key, value in fields.items():
            setattr(obj, key, value)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def delete_by_pk(self, pk: Any) -> bool:
        pk_columns = list(self.model.__table__.primary_key.columns)
        if len(pk_columns) != 1:
            raise ValueError("Composite primary keys are not supported in delete_by_pk")
        result = await self._session.execute(delete(self.model).where(pk_columns[0] == pk))
        await self._session.flush()
        return result.rowcount > 0
