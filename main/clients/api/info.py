from __future__ import annotations

from services.clients.service import ClientService
from shared.bot.session import resolve_session
from .exceptions import ApiNotFoundError
from .schemas import AgreementInfo


class InfoApi:
    async def get_agreement(self, user_id: int) -> AgreementInfo:
        async with resolve_session() as session:
            cs = ClientService(session)
            ag = await cs.get_active_agreement(user_id)
            if not ag:
                raise ApiNotFoundError("Agreement not found")
            return AgreementInfo(
                agreement_id=ag.agreement_id,
                title=ag.title,
                document_url=ag.document_url,
            )
