"""
Transaction management utilities for SQLAlchemy async sessions.

Provides explicit transaction boundaries for domain service operations.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def transaction(session: "AsyncSession"):
    """
    Async context manager for explicit transaction boundaries.

    Usage:
        async with transaction(session):
            # perform multiple repository operations
            await repo1.create(...)
            await repo2.update(...)
            # commit happens automatically on exit

    On exception, the transaction is rolled back automatically.

    Args:
        session: SQLAlchemy async session

    Yields:
        The same session for use within the transaction block
    """
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
