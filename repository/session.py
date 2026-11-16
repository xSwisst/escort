from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from shared.db.engine import create_db


class Database:
    def __init__(self, db_url: str, echo: bool = False, pool_size: int = 10, max_overflow: int = 20) -> None:
        self.engine, self.session_maker, self._get_session = create_db(
            db_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

    def session(self) -> AsyncSession:
        return self.session_maker()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async for session in self._get_session():
            yield session

    async def close(self) -> None:
        await self.engine.dispose()
