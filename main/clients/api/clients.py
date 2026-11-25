from __future__ import annotations

from services.clients.service import ClientService
from shared.bot.session import resolve_session
from .schemas import ActionStatusResponse, AgreementInfo, ClientCities, ClientIdentity, StartBootstrapResponse


class ClientApi:
    async def bootstrap(
        self,
        *,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        admin_id: int | None = None,
    ) -> StartBootstrapResponse:
        async with resolve_session() as session:
            cs = ClientService(session)
            res = await cs.bootstrap(
                user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                admin_id=admin_id,
            )
            ag_info = None
            if res.agreement:
                ag_info = AgreementInfo(
                    agreement_id=res.agreement.agreement_id,
                    title=res.agreement.title,
                    document_url=res.agreement.document_url,
                )
            return StartBootstrapResponse(
                client=ClientIdentity(
                    user_id=res.client.user_id,
                    has_accepted_agreement=res.client.has_accepted_agreement,
                ),
                agreement_required=res.agreement_required,
                agreement=ag_info,
            )

    async def accept_agreement(self, user_id: int) -> None:
        async with resolve_session() as session:
            cs = ClientService(session)
            await cs.accept_agreement(user_id)

    async def get_cities(self, user_id: int) -> ClientCities:
        async with resolve_session() as session:
            cs = ClientService(session)
            client = await cs.get_client(user_id)
            active_slot = int(getattr(client, "active_city_slot", 1) or 1)
            active_city = client.secondary_city if active_slot == 2 and client.secondary_city else (client.primary_city if client else None)
            return ClientCities(
                primary_city=client.primary_city if client else None,
                secondary_city=client.secondary_city if client else None,
                active_city_slot=active_slot,
                active_city=active_city,
            )

    async def set_city(self, user_id: int, *, city: str, slot: int) -> ClientCities:
        async with resolve_session() as session:
            cs = ClientService(session)
            await cs.set_city(user_id, city, slot)
            return await self.get_cities(user_id)

    async def switch_city(self, user_id: int, *, active_city_slot: int) -> ClientCities:
        async with resolve_session() as session:
            cs = ClientService(session)
            await cs.switch_city(user_id, active_city_slot)
            return await self.get_cities(user_id)
