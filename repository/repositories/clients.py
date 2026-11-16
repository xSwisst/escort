from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from repository.models.clients import Client
from repositories.base import BaseRepository


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
    ) -> Client | None:
        """
        Get a client by user_id with optional eager loading of relationships.

        Args:
            pk: User ID
            include_orders: Load orders relationship
            include_addresses: Load addresses relationship
            include_agreement: Load agreement relationship
            include_promo: Load promo relationship

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
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        user_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ) -> tuple[Client, bool]:
        client = await self.get(user_id)
        if client:
            updates: dict[str, str | None] = {}
            if first_name is not None and client.first_name != first_name:
                updates["first_name"] = first_name
            if last_name is not None and client.last_name != last_name:
                updates["last_name"] = last_name
            if username is not None and client.username != username:
                updates["username"] = username
            if updates:
                client = await self.update_by_user_id(user_id, **updates) or client
            return client, False
        return await self.create(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
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

    async def set_agreement(self, user_id: int, agreement_id: str) -> None:
        await self.update_by_user_id(user_id, has_accepted_agreement=True, agreement_id=agreement_id)

    async def set_city(self, user_id: int, city: str, slot: int = 1) -> None:
        fields = {"primary_city": city} if slot == 1 else {"secondary_city": city}
        fields["active_city_slot"] = slot
        await self.update_by_user_id(user_id, **fields)

    async def count_registered(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Client))
        return result.scalar_one()

    async def search(self, query: str | None, *, page: int = 1, per_page: int = 20) -> tuple[list[Client], int]:
        page = max(1, int(page or 1))
        per_page = max(1, min(100, int(per_page or 20)))

        base_stmt = select(Client)
        count_stmt = select(func.count()).select_from(Client)

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
