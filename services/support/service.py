from sqlalchemy.ext.asyncio import AsyncSession

from repository.repositories.agreements import AgreementRepository
from repository.repositories.clients import ClientRepository
from repository.repositories.support_messages import SupportMessageRepository
from repository.repositories.support_threads import SupportThreadRepository


class SupportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.clients = ClientRepository(session)
        self.agreements = AgreementRepository(session)
        self.threads = SupportThreadRepository(session)
        self.messages = SupportMessageRepository(session)

    async def get_client_summary(self, user_id: int):
        client = await self.clients.get(user_id)
        if not client:
            return None
        agreement = await self.agreements.get(client.agreement_id) if client.agreement_id else None
        thread = await self.threads.get_by_user(user_id)
        return {
            "client": client,
            "agreement": agreement,
            "thread": thread,
        }

    async def count_user_messages(self, user_id: int) -> int:
        return await self.messages.count_by_user(user_id)
