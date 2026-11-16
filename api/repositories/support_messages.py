from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.support import SupportMessage
from repositories.base import BaseRepository


class SupportMessageRepository(BaseRepository[SupportMessage]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SupportMessage)

    async def get_by_support_message(self, forum_chat_id: int, support_message_id: int) -> SupportMessage | None:
        result = await self._session.execute(
            select(SupportMessage)
            .where(
                SupportMessage.forum_chat_id == forum_chat_id,
                SupportMessage.forum_message_id == support_message_id,
            )
            .order_by(SupportMessage.id.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_user_message(self, user_id: int, user_message_id: int) -> SupportMessage | None:
        result = await self._session.execute(
            select(SupportMessage)
            .where(
                SupportMessage.user_id == user_id,
                SupportMessage.client_message_id == user_message_id,
            )
            .order_by(SupportMessage.id.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def count_by_user(self, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count(SupportMessage.id)).where(SupportMessage.user_id == user_id)
        )
        return result.scalar() or 0
