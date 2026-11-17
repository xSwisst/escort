from __future__ import annotations

from typing import Any
from datetime import datetime
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.client_activity_logs import ClientActivityLog
from repository.models.clients import Client
from repository.repositories.base import BaseRepository


class ClientActivityLogRepository(BaseRepository[ClientActivityLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ClientActivityLog)

    async def create_log(
        self,
        *,
        user_id: int,
        client_id: int | None = None,
        event_type: str,
        title: str,
        description: str | None = None,
        payload: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> ClientActivityLog:
        # If client_id is not provided, try to resolve from Client table
        if client_id is None:
            stmt = select(Client.id).where(Client.user_id == user_id)
            res = await self._session.execute(stmt)
            client_id = res.scalar_one_or_none()

        log_entry = ClientActivityLog(
            user_id=user_id,
            client_id=client_id,
            event_type=event_type,
            title=title,
            description=description,
            payload=payload or {},
        )
        if created_at is not None:
            log_entry.created_at = created_at

        self._session.add(log_entry)
        await self._session.commit()
        await self._session.refresh(log_entry)
        return log_entry

    async def get_by_id(self, log_id: int) -> ClientActivityLog | None:
        stmt = select(ClientActivityLog).where(ClientActivityLog.id == log_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def has_user_event(self, user_id: int, event_type: str) -> bool:
        stmt = select(func.count(ClientActivityLog.id)).where(
            ClientActivityLog.user_id == user_id,
            ClientActivityLog.event_type == event_type,
        )
        res = await self._session.execute(stmt)
        count = res.scalar_one_or_none() or 0
        return count > 0

    async def get_by_client_paginated(
        self,
        identifier: int,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[ClientActivityLog], int]:
        # Filter by either user_id or client_id
        # Telegram user IDs exceed int32 max (2.14B), while internal serial client_id is int32
        INT32_MAX = 2_147_483_647
        if identifier > INT32_MAX:
            base_filter = (ClientActivityLog.user_id == identifier)
        else:
            base_filter = or_(
                ClientActivityLog.user_id == identifier,
                ClientActivityLog.client_id == identifier,
            )

        conditions = [base_filter]
        if query and query.strip():
            clean_q = query.strip()
            conditions.append(
                or_(
                    ClientActivityLog.title.ilike(f"%{clean_q}%"),
                    ClientActivityLog.description.ilike(f"%{clean_q}%"),
                    ClientActivityLog.event_type.ilike(f"%{clean_q}%"),
                )
            )

        # Count total
        count_stmt = select(func.count(ClientActivityLog.id)).where(*conditions)
        total_res = await self._session.execute(count_stmt)
        total = total_res.scalar_one_or_none() or 0

        # Items
        offset = max(0, (page - 1) * per_page)
        stmt = (
            select(ClientActivityLog)
            .where(*conditions)
            .order_by(ClientActivityLog.created_at.desc(), ClientActivityLog.id.desc())
            .offset(offset)
            .limit(per_page)
        )
        items_res = await self._session.execute(stmt)
        items = list(items_res.scalars().all())

        return items, total
