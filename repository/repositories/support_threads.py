from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.support import SupportThread
from repository.repositories.base import BaseRepository


class SupportThreadRepository(BaseRepository[SupportThread]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SupportThread)

    async def get_by_user(self, user_id: int) -> SupportThread | None:
        return await self.get_by(user_id=user_id)

    async def get_by_topic(self, forum_chat_id: int, topic_id: int) -> SupportThread | None:
        return await self.get_by(forum_chat_id=forum_chat_id, forum_topic_id=topic_id)

    async def upsert_thread(
        self,
        *,
        user_id: int,
        forum_chat_id: int,
        topic_id: int,
        info_message_id: int | None = None,
    ) -> SupportThread:
        thread = await self.get_by_user(user_id)
        fields = {
            "forum_chat_id": forum_chat_id,
            "forum_topic_id": topic_id,
        }
        if info_message_id is not None:
            fields["pinned_info_message_id"] = info_message_id
        if thread:
            return await self.update_by_pk(thread.id, **fields) or thread
        return await self.create(user_id=user_id, **fields)

    async def list_banned(self) -> list[SupportThread]:
        result = await self._session.execute(select(SupportThread).where(SupportThread.is_banned == True))  # noqa: E712
        return list(result.scalars().all())
