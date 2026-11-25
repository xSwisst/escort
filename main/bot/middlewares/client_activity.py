from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from repository.models.clients import Client
from shared.utils.time import now_msk

logger = logging.getLogger(__name__)


class ClientActivityMiddleware(BaseMiddleware):
    """
    Records the timestamp of every client action (message, callback_query,
    inline_query) into `clients.last_active_at` without blocking handlers.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self._session_maker = session_maker
        self._tasks: set[asyncio.Task[None]] = set()

    async def close(self) -> None:
        for task in list(self._tasks):
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _touch_activity(self, user_id: int) -> None:
        try:
            async with self._session_maker() as session:
                await session.execute(
                    update(Client)
                    .where(Client.user_id == user_id)
                    .values(last_active_at=now_msk())
                )
                await session.commit()
        except Exception as exc:
            logger.debug("ClientActivityMiddleware: failed to update last_active_at for user_id=%s: %s", user_id, exc)

    def _schedule_touch(self, user_id: int) -> None:
        task = asyncio.create_task(self._touch_activity(user_id))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: User | None = getattr(event, "from_user", None)
        try:
            return await handler(event, data)
        finally:
            if tg_user is not None and not tg_user.is_bot:
                self._schedule_touch(tg_user.id)
