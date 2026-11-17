from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from shared.bot.middleware import get_current_session


@asynccontextmanager
async def resolve_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Resolve the current active AsyncSession from the aiogram event context.
    If called outside an aiogram event, opens a standalone session.
    """
    session = get_current_session()
    if session is not None:
        yield session
    else:
        import os
        from repository.session import Database

        db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
        db = Database(db_url)
        async with db.session_maker() as new_session:
            try:
                yield new_session
                await new_session.commit()
            except Exception:
                await new_session.rollback()
                raise
