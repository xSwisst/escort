from datetime import timedelta
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from repository.models.clients import Client
from repository.repositories.base import BaseRepository
from shared.utils.time import now_msk


class ClientRepository(BaseRepository[Client]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Client)

    async def get(
        self,
        pk,
        *,
        include_orders: bool = False,
        include_addresses: bool = False,
        include_agreement: bool = False,
        include_promo: bool = False,
        include_admin: bool = False,
    ) -> Client | None:
        """
        Get a client by user_id with optional eager loading of relationships.

        Args:
            pk: User ID
            include_orders: Load orders relationship
            include_addresses: Load addresses relationship
            include_agreement: Load agreement relationship
            include_promo: Load promo relationship
            include_admin: Load admin relationship

        Returns:
            Client instance or None
        """
        stmt = select(Client).where(Client.user_id == pk)

        if include_orders:
            stmt = stmt.options(selectinload(Client.orders))
        if include_addresses:
            stmt = stmt.options(selectinload(Client.addresses))
        if include_agreement:
            stmt = stmt.options(selectinload(Client.agreement))
        if include_promo:
            stmt = stmt.options(selectinload(Client.promo))
        if include_admin:
            stmt = stmt.options(selectinload(Client.admin))

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_db_id(
        self,
        db_id: int,
        *,
        include_orders: bool = False,
        include_addresses: bool = False,
        include_agreement: bool = False,
        include_promo: bool = False,
        include_admin: bool = False,
    ) -> Client | None:
        stmt = select(Client).where(Client.id == db_id)
        if include_orders:
            stmt = stmt.options(selectinload(Client.orders))
        if include_addresses:
            stmt = stmt.options(selectinload(Client.addresses))
        if include_agreement:
            stmt = stmt.options(selectinload(Client.agreement))
        if include_promo:
            stmt = stmt.options(selectinload(Client.promo))
        if include_admin:
            stmt = stmt.options(selectinload(Client.admin))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        user_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        admin_id: int | None = None,
    ) -> tuple[Client, bool]:
        client = await self.get(user_id)
        if client:
            updates: dict[str, object] = {}
            if first_name is not None and client.first_name != first_name:
                updates["first_name"] = first_name
            if last_name is not None and client.last_name != last_name:
                updates["last_name"] = last_name
            if username is not None and client.username != username:
                updates["username"] = username
            if client.admin_id is None and admin_id is not None:
                updates["admin_id"] = admin_id
            if updates:
                client = await self.update_by_user_id(user_id, **updates) or client
            return client, False
        return await self.create(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            admin_id=admin_id,
        ), True

    async def update_by_user_id(self, user_id: int, **fields):
        client = await self.get(user_id)
        if client is None:
            return None
        for key, value in fields.items():
            setattr(client, key, value)
        await self._session.flush()
        await self._session.refresh(client)
        return client

    async def set_agreement(self, user_id: int, agreement_id: str | None = None) -> None:
        await self.update_by_user_id(user_id, has_accepted_agreement=True, agreement_id=agreement_id)

    async def set_city(self, user_id: int, city: str, slot: int = 1) -> None:
        fields: dict[str, object] = {"active_city_slot": slot}
        if slot == 1:
            fields["primary_city"] = city
        elif slot == 2:
            fields["secondary_city"] = city
        await self.update_by_user_id(user_id, **fields)

    async def count_registered(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Client))
        return result.scalar_one()

    async def search(
        self,
        query: str | None,
        *,
        page: int = 1,
        per_page: int = 20,
        admin_id: int | None = None,
    ) -> tuple[list[Client], int]:
        page = max(1, int(page or 1))
        per_page = max(1, min(100, int(per_page or 20)))

        base_stmt = select(Client)
        count_stmt = select(func.count()).select_from(Client)

        if admin_id is not None:
            base_stmt = base_stmt.where(Client.admin_id == admin_id)
            count_stmt = count_stmt.where(Client.admin_id == admin_id)

        normalized_query = (query or "").strip()
        if normalized_query:
            pattern = f"%{normalized_query.lower()}%"
            filters = or_(
                cast(Client.user_id, String).ilike(pattern),
                Client.first_name.ilike(pattern),
                Client.last_name.ilike(pattern),
                Client.username.ilike(pattern),
                Client.primary_city.ilike(pattern),
                Client.secondary_city.ilike(pattern),
            )
            base_stmt = base_stmt.where(filters)
            count_stmt = count_stmt.where(filters)

        base_stmt = base_stmt.order_by(Client.registered_at.desc()).offset((page - 1) * per_page).limit(per_page)
        items = list((await self._session.execute(base_stmt)).scalars().all())
        total = int((await self._session.execute(count_stmt)).scalar_one())
        return items, total

    async def get_stats_by_admin(self, admin_id: int) -> dict[str, int]:
        now = now_msk()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_res = await self._session.execute(
            select(func.count()).select_from(Client).where(Client.admin_id == admin_id)
        )
        today_res = await self._session.execute(
            select(func.count())
            .select_from(Client)
            .where(Client.admin_id == admin_id, Client.registered_at >= today_start)
        )
        month_res = await self._session.execute(
            select(func.count())
            .select_from(Client)
            .where(Client.admin_id == admin_id, Client.registered_at >= month_start)
        )
        return {
            "today": int(today_res.scalar_one() or 0),
            "month": int(month_res.scalar_one() or 0),
            "all": int(total_res.scalar_one() or 0),
        }

    async def get_broadcast_recipients(self, admin_id: int, audience: str = "all") -> list[int]:
        stmt = select(Client.user_id).where(
            Client.admin_id == admin_id,
            Client.is_banned.is_(False),
        )
        days_map = {"new7": 7, "new14": 14, "new30": 30}
        if audience in days_map:
            cutoff = now_msk() - timedelta(days=days_map[audience])
            stmt = stmt.where(Client.registered_at >= cutoff)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
