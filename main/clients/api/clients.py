from __future__ import annotations

from clients.logs import emit_log_event
from repository.repositories.client_logs import ClientActivityLogRepository
from services.clients.service import ClientService
from shared.bot.session import resolve_session
from .schemas import ActionStatusResponse, AgreementInfo, ClientCities, ClientCityItem, ClientIdentity, StartBootstrapResponse


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
            activity_repo = ClientActivityLogRepository(session)
            has_new_user_log = await activity_repo.has_user_event(user_id, "new_user")
            ag_info = None
            if res.agreement:
                ag_info = AgreementInfo(
                    agreement_id=res.agreement.agreement_id,
                    title=res.agreement.title,
                    document_url=res.agreement.document_url,
                )
            out = StartBootstrapResponse(
                client=ClientIdentity(
                    user_id=res.client.user_id,
                    has_accepted_agreement=res.client.has_accepted_agreement,
                ),
                agreement_required=res.agreement_required,
                agreement=ag_info,
            )
            if not has_new_user_log:
                await emit_log_event(
                    "new_user",
                    user_id,
                    {
                        "id": res.client.id,
                        "user_id": res.client.user_id,
                        "first_name": res.client.first_name or "",
                        "last_name": res.client.last_name or "",
                        "username": res.client.username,
                        "admin_id": res.client.admin_id,
                    },
                )
            return out

    async def accept_agreement(self, user_id: int) -> None:
        async with resolve_session() as session:
            cs = ClientService(session)
            client = await cs.get_client(user_id)
            agreement = await cs.get_active_agreement(user_id)
            await cs.accept_agreement(user_id)
            if client:
                await emit_log_event(
                    "agreement_accepted",
                    user_id,
                    {
                        "id": client.id,
                        "user_id": client.user_id,
                        "first_name": client.first_name or "",
                        "last_name": client.last_name or "",
                        "username": client.username,
                        "admin_id": client.admin_id,
                        "agreement_id": getattr(agreement, "agreement_id", None),
                    },
                )

    async def get_cities(self, user_id: int) -> ClientCities:
        async with resolve_session() as session:
            cs = ClientService(session)
            profile = await cs.get_profile(user_id)
            return ClientCities(
                primary_city=profile.primary_city,
                secondary_city=profile.secondary_city,
                active_city_slot=profile.active_city_slot,
                active_city=profile.city,
                cities=[
                    ClientCityItem(slot=c.slot, city_name=c.city_name, is_active=c.is_active)
                    for c in (profile.cities or [])
                ],
            )

    async def has_city(self, user_id: int, city: str) -> bool:
        async with resolve_session() as session:
            cs = ClientService(session)
            return await cs.has_city(user_id, city)

    async def set_city(self, user_id: int, *, city: str, slot: int) -> ClientCities:
        async with resolve_session() as session:
            cs = ClientService(session)
            client = await cs.get_client(user_id)
            old_city = (client.primary_city if slot == 1 else client.secondary_city) if client else None
            await cs.set_city(user_id, city, slot)
            result = await self.get_cities(user_id)
            if client:
                event_type = "change_of_city" if old_city else "add_city"
                await emit_log_event(
                    event_type,
                    user_id,
                    {
                        "id": client.id,
                        "user_id": client.user_id,
                        "first_name": client.first_name or "",
                        "last_name": client.last_name or "",
                        "username": client.username,
                        "admin_id": client.admin_id,
                        "city": city,
                        "old_city": old_city or "—",
                        "new_city": city,
                    },
                )
            return result

    async def switch_city(self, user_id: int, *, active_city_slot: int) -> ClientCities:
        async with resolve_session() as session:
            cs = ClientService(session)
            before = await self.get_cities(user_id)
            await cs.switch_city(user_id, active_city_slot)
            after = await self.get_cities(user_id)
            client = await cs.get_client(user_id)
            if client and after.active_city:
                await emit_log_event(
                    "change_of_city",
                    user_id,
                    {
                        "id": client.id,
                        "user_id": client.user_id,
                        "first_name": client.first_name or "",
                        "last_name": client.last_name or "",
                        "username": client.username,
                        "admin_id": client.admin_id,
                        "city": after.active_city,
                        "old_city": before.active_city or "—",
                        "new_city": after.active_city,
                    },
                )
            return after
