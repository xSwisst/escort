from __future__ import annotations

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.admins import Admin
from repository.models.cards import Card
from repository.models.promos import Promo
from repository.models.settings import Agreement
from repository.repositories.admins import AdminRepository
from repository.repositories.cards import CardRepository
from repository.repositories.promos import PromoRepository
from repository.repositories.agreements import AgreementRepository
from repository.repositories.clients import ClientRepository
from repository.repositories.client_logs import ClientLogRepository
from services.forms.admin_service import AdminFormsService


class AdminService:
    """Unified service for admin operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.admins = AdminRepository(session)
        self.cards = CardRepository(session)
        self.promos = PromoRepository(session)
        self.agreements = AgreementRepository(session)
        self.clients = ClientRepository(session)
        self.client_logs = ClientLogRepository(session)
        self.forms = AdminFormsService(session)

    # --- Admins / Workers ---
    async def get_or_create_admin(
        self,
        telegram_id: int,
        *,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Admin:
        admin, _ = await self.admins.get_or_create(
            telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        return admin

    async def get_admin_by_telegram_id(self, telegram_id: int) -> Admin | None:
        return await self.admins.get_by_telegram_id(telegram_id)

    # --- Cards ---
    async def list_cards(self, include_deleted: bool = False) -> list[Card]:
        return await self.cards.list_cards(include_deleted=include_deleted)

    async def create_card(self, *, card_number: str, min_amount: int, max_amount: int, created_by: int | None = None) -> Card:
        return await self.cards.create_card(
            card_number=card_number,
            min_amount=min_amount,
            max_amount=max_amount,
            created_by=created_by,
        )

    async def toggle_card(self, card_id: int) -> Card | None:
        return await self.cards.toggle_active(card_id)

    async def delete_card(self, card_id: int) -> bool:
        return await self.cards.soft_delete(card_id)

    # --- Promos ---
    async def list_promos(self, *, admin_id: int | None = None) -> list[Promo]:
        return await self.promos.list_by_admin(admin_id=admin_id)

    async def create_promo(self, *, code: str, discount_amount: int, admin_id: int | None = None) -> Promo:
        return await self.promos.create(code=code, discount_amount=discount_amount, admin_id=admin_id)

    async def delete_promo(self, promo_id: int) -> bool:
        return await self.promos.delete_by_pk(promo_id)

    # --- Agreements ---
    async def list_agreements(self) -> list[Agreement]:
        return await self.agreements.get_all()

    async def create_agreement(self, *, agreement_id: str, title: str, document_url: str | None = None) -> Agreement:
        return await self.agreements.create(
            agreement_id=agreement_id,
            title=title,
            document_url=document_url,
        )

    async def delete_agreement(self, agreement_id: str) -> bool:
        return await self.agreements.delete_by_pk(agreement_id)

    # --- Clients ---
    async def list_clients(self, page: int = 1, page_size: int = 20, search: str | None = None, *, admin_id: int | None = None):
        return await self.clients.search(search, page=page, per_page=page_size, admin_id=admin_id)

    async def get_client_stats_by_admin(self, admin_id: int) -> dict[str, int]:
        return await self.clients.get_stats_by_admin(admin_id)

    async def get_broadcast_recipients(self, admin_id: int, audience: str = "all") -> list[int]:
        return await self.clients.get_broadcast_recipients(admin_id, audience=audience)

    async def get_client(self, user_id: int):
        return await self.clients.get(user_id)

    async def get_client_by_db_id(self, db_id: int):
        return await self.clients.get_by_db_id(db_id)

    async def set_ban(self, user_id: int, is_banned: bool):
        return await self.clients.set_ban(user_id, is_banned)

    async def set_agreement_for_user(self, user_id: int, agreement_id: str):
        return await self.clients.set_agreement(user_id, agreement_id)

    async def list_client_logs(self, user_id: int, limit: int = 50):
        return await self.client_logs.get_by_user(user_id, limit=limit)
