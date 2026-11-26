from __future__ import annotations

from typing import Any

import httpx

from core.settings import settings
from services.admin_service import AdminService
from shared.bot.session import resolve_session
from .exceptions import ApiNotFoundError
from .schemas import (
    ActionStatusResponse,
    AdditionalItem,
    AdditionalsListResponse,
    AdminClientDetailResponse,
    AdminClientItem,
    AdminClientListResponse,
    AdminClientLogDetailResponse,
    AdminClientLogItem,
    AdminClientLogsResponse,
    AdminInfo,
    AgreementItem,
    AgreementsResponse,
    BroadcastResponse,
    CardItem,
    CardsListResponse,
    FormDetailResponse,
    FormListItem,
    FormsListResponse,
    MainBotInfo,
    PromoItem,
    PromosListResponse,
    ReviewItem,
    ReviewsListResponse,
    ServiceItem,
    ServicesListResponse,
    WorkerClientStats,
)


class AdminApi:
    # ── Workers / Admins & Main Bot Meta ──────────────────────────────────────

    async def get_or_create_admin(
        self,
        telegram_id: int,
        *,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> AdminInfo:
        async with resolve_session() as session:
            admin_svc = AdminService(session)
            a = await admin_svc.get_or_create_admin(
                telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            return AdminInfo(
                id=a.id,
                telegram_id=a.telegram_id,
                username=a.username,
                first_name=a.first_name,
                last_name=a.last_name,
                created_at=a.created_at,
            )

    async def get_main_bot_info(self) -> MainBotInfo:
        url = f"{settings.MAIN_BOT_URL.rstrip('/')}/internal/v1/bot-info"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    return MainBotInfo(**data)
        except Exception:
            pass
        return MainBotInfo(is_alive=False)

    async def get_worker_client_stats(self, admin_id: int) -> WorkerClientStats:
        async with resolve_session() as session:
            admin = AdminService(session)
            stats = await admin.get_client_stats_by_admin(admin_id)
            return WorkerClientStats(**stats)

    # ── Clients ──────────────────────────────────────────────────────────────

    async def list_clients(
        self,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
        admin_id: int | None = None,
    ) -> AdminClientListResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            items, total = await admin.clients.search(query, page=page, per_page=per_page, admin_id=admin_id)
            return AdminClientListResponse(
                items=[
                    AdminClientItem(
                        id=c.id,
                        user_id=c.user_id,
                        first_name=c.first_name,
                        last_name=c.last_name,
                        username=c.username,
                        avatar_url=getattr(c, "avatar_url", None),
                        primary_city=c.primary_city,
                        secondary_city=c.secondary_city,
                        active_city_slot=c.active_city_slot,
                        active_city=(c.secondary_city if int(c.active_city_slot or 1) == 2 and c.secondary_city else (c.primary_city or c.secondary_city)),
                        balance=c.balance,
                        is_banned=bool(c.is_banned),
                        is_pinned=bool(getattr(c, "is_pinned", False)),
                        registered_at=c.registered_at,
                        last_active_at=getattr(c, "last_active_at", None),
                    )
                    for c in items
                ],
                total=total,
                page=page,
                per_page=per_page,
            )

    @staticmethod
    async def _build_client_detail(session, c) -> AdminClientDetailResponse:
        from sqlalchemy import func, select
        from repository.models.addresses import Address
        from repository.models.forms import FormFavorite
        from repository.models.orders import Order

        orders_count = int((await session.execute(select(func.count()).select_from(Order).where(Order.user_id == c.user_id))).scalar_one() or 0)
        addresses_count = int((await session.execute(select(func.count()).select_from(Address).where(Address.user_id == c.user_id))).scalar_one() or 0)
        favorites_count = int((await session.execute(select(func.count()).select_from(FormFavorite).where(FormFavorite.user_id == c.user_id))).scalar_one() or 0)
        active_city = c.secondary_city if int(c.active_city_slot or 1) == 2 and c.secondary_city else (c.primary_city or c.secondary_city)
        return AdminClientDetailResponse(
            id=c.id,
            user_id=c.user_id,
            first_name=c.first_name,
            last_name=c.last_name,
            username=c.username,
            avatar_url=getattr(c, "avatar_url", None),
            primary_city=c.primary_city,
            secondary_city=c.secondary_city,
            active_city_slot=c.active_city_slot,
            active_city=active_city,
            balance=int(c.balance or 0),
            rating=float(c.rating or 0.0),
            promo=c.promo_code,
            has_accepted_agreement=bool(c.has_accepted_agreement),
            agreement_id=c.agreement_id,
            title=c.agreement.title if c.agreement else None,
            document_url=c.agreement.document_url if c.agreement else None,
            is_banned=bool(c.is_banned),
            is_pinned=bool(getattr(c, "is_pinned", False)),
            orders_count=orders_count,
            addresses_count=addresses_count,
            favorites_count=favorites_count,
            registered_at=c.registered_at,
            last_active_at=getattr(c, "last_active_at", None),
        )

    async def get_client(self, user_id: int, *, admin_id: int | None = None) -> AdminClientDetailResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            c = await admin.clients.get(user_id, include_agreement=True)
            if not c or (admin_id is not None and c.admin_id != admin_id):
                raise ApiNotFoundError(f"Client not found: {user_id}")
            return await self._build_client_detail(session, c)

    async def get_client_by_db_id(self, db_id: int, *, admin_id: int | None = None) -> AdminClientDetailResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            c = await admin.clients.get_by_db_id(db_id, include_agreement=True)
            if not c or (admin_id is not None and c.admin_id != admin_id):
                raise ApiNotFoundError(f"Client not found by db_id: {db_id}")
            return await self._build_client_detail(session, c)

    async def set_ban(self, *, user_id: int, is_banned: bool) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.clients.update_by_user_id(user_id, is_banned=is_banned)
            return ActionStatusResponse(ok=True)

    async def toggle_pin(self, *, user_id: int) -> bool:
        async with resolve_session() as session:
            admin = AdminService(session)
            c = await admin.clients.get(user_id)
            if not c:
                raise ApiNotFoundError(f"Client not found: {user_id}")
            new_pinned = not bool(getattr(c, "is_pinned", False))
            await admin.clients.update_by_user_id(user_id, is_pinned=new_pinned)
            return new_pinned

    async def set_agreement(self, *, user_id: int, agreement_id: str) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.clients.set_agreement(user_id, agreement_id)
            return ActionStatusResponse(ok=True)

    async def send_message_to_client(self, *, user_id: int, text: str) -> ActionStatusResponse:
        url = f"{settings.MAIN_BOT_URL.rstrip('/')}/internal/v1/notify/direct-message"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json={"user_id": user_id, "text": text})
                if resp.status_code == 200 and resp.json().get("ok"):
                    return ActionStatusResponse(ok=True)
        except Exception:
            pass
        return ActionStatusResponse(ok=False)

    async def adjust_balance(
        self,
        *,
        user_id: int,
        action: str,
        amount: int,
        notify: bool = False,
    ) -> int:
        from repository.models.payments import Transaction, TransactionType

        async with resolve_session() as session:
            admin = AdminService(session)
            c = await admin.clients.get(user_id)
            if not c:
                raise ApiNotFoundError(f"Client not found: {user_id}")
            old_balance = int(c.balance or 0)
            if action == "set":
                new_balance = max(0, int(amount))
            elif action == "add":
                new_balance = max(0, old_balance + int(amount))
            elif action == "sub":
                new_balance = max(0, old_balance - int(amount))
            else:
                raise ValueError(f"Unknown balance action: {action}")

            delta = new_balance - old_balance
            await admin.clients.update_by_user_id(user_id, balance=new_balance)
            session.add(
                Transaction(
                    user_id=user_id,
                    type=TransactionType.ADMIN_ADJUST,
                    amount=delta,
                    balance_after=new_balance,
                    description="Корректировка баланса администратором",
                )
            )
            await session.flush()

        if notify:
            sign = "+" if delta >= 0 else ""
            await self.send_message_to_client(
                user_id=user_id,
                text=(
                    f"💳 <b>Ваш баланс обновлён</b>\n\n"
                    f"Изменение: <b>{sign}{delta} RUB</b>\n"
                    f"Текущий баланс: <b>{new_balance} RUB</b>"
                ),
            )
        return new_balance

    async def get_client_orders(self, user_id: int, *, search: str = "", offset: int = 0, limit: int = 20) -> list[dict]:
        from sqlalchemy import select
        from repository.models.orders import Order

        async with resolve_session() as session:
            stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
            rows = list((await session.execute(stmt)).scalars().all())
            q = search.strip().lower()
            items = []
            for o in rows:
                status_val = o.status.value if hasattr(o.status, "value") else str(o.status or "")
                model_info = o.form_snapshot or o.form_code or "Анкета"
                city = o.city_name or "—"
                if q and q not in str(o.id) and q not in model_info.lower() and q not in city.lower() and q not in status_val.lower():
                    continue
                items.append({
                    "id": o.id,
                    "status": status_val,
                    "model_info": model_info,
                    "city": city,
                    "tariff": o.tariff_name or "—",
                    "created_at_dt": o.created_at,
                })
            return items[offset : offset + limit]

    async def get_client_transactions(self, user_id: int, *, search: str = "", offset: int = 0, limit: int = 20) -> list[dict]:
        from sqlalchemy import select
        from repository.models.payments import Transaction

        async with resolve_session() as session:
            stmt = select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.created_at.desc())
            rows = list((await session.execute(stmt)).scalars().all())
            q = search.strip().lower()
            items = []
            for tx in rows:
                tx_type = tx.type.value if hasattr(tx.type, "value") else str(tx.type or "")
                if q and q not in str(tx.id) and q not in (tx.description or "").lower() and q not in tx_type.lower():
                    continue
                items.append({
                    "id": tx.id,
                    "type": tx_type,
                    "amount": tx.amount,
                    "balance_after": tx.balance_after,
                    "description": tx.description,
                    "created_at_dt": tx.created_at,
                })
            return items[offset : offset + limit]

    async def get_client_payments(self, user_id: int, *, search: str = "", offset: int = 0, limit: int = 20) -> list[dict]:
        from sqlalchemy import select
        from repository.models.payments import PaymentInvoice

        async with resolve_session() as session:
            stmt = select(PaymentInvoice).where(PaymentInvoice.user_id == user_id).order_by(PaymentInvoice.created_at.desc())
            rows = list((await session.execute(stmt)).scalars().all())
            q = search.strip().lower()
            items = []
            for inv in rows:
                st = inv.status.value if hasattr(inv.status, "value") else str(inv.status or "")
                if q and q not in str(inv.id) and q not in (inv.invoice_number or "").lower() and q not in st.lower():
                    continue
                items.append({
                    "id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "status": st,
                    "amount": inv.amount,
                    "payment_method": inv.payment_method,
                    "created_at_dt": inv.created_at,
                })
            return items[offset : offset + limit]

    async def list_client_logs(
        self,
        client_id: int | str,
        *,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> AdminClientLogsResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            items, total = await admin.client_logs.get_by_client_paginated(
                int(client_id), query=query, page=page, per_page=per_page
            )
            return AdminClientLogsResponse(
                items=[
                    AdminClientLogItem(
                        id=log.id,
                        user_id=log.user_id,
                        client_id=log.client_id,
                        event_type=log.event_type,
                        title=log.title,
                        description=log.description,
                        payload=log.payload or {},
                        created_at=log.created_at,
                    )
                    for log in items
                ],
                total=total,
                page=page,
                per_page=per_page,
            )

    async def get_client_log(self, log_id: int) -> AdminClientLogDetailResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            log = await admin.client_logs.get_by_id(log_id)
            if not log:
                raise ApiNotFoundError(f"Log not found: {log_id}")
            return AdminClientLogDetailResponse(
                id=log.id,
                user_id=log.user_id,
                client_id=log.client_id,
                event_type=log.event_type,
                title=log.title,
                description=log.description,
                payload=log.payload or {},
                created_at=log.created_at,
            )

    async def start_broadcast(self, payload: dict[str, Any]) -> BroadcastResponse:
        url = f"{settings.MAIN_BOT_URL.rstrip('/')}/internal/v1/broadcast"
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return BroadcastResponse(
                sent=int(data.get("sent", 0)),
                failed=int(data.get("failed", 0)),
                total=int(data.get("total", 0)),
                total_queued=int(data.get("total_queued", 0)),
                success=bool(data.get("success", True)),
            )

    # ── Agreements ────────────────────────────────────────────────────────────

    async def list_agreements(self) -> AgreementsResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            agreements = await admin.list_agreements()
            return AgreementsResponse(
                items=[
                    AgreementItem(
                        agreement_id=a.agreement_id,
                        title=a.title,
                        document_url=a.document_url,
                    )
                    for a in agreements
                ]
            )

    async def create_agreement(self, payload: dict[str, Any]) -> AgreementItem:
        async with resolve_session() as session:
            admin = AdminService(session)
            a = await admin.agreements.create(**payload)
            return AgreementItem(
                agreement_id=a.agreement_id,
                title=a.title,
                document_url=a.document_url,
            )

    async def delete_agreement(self, agreement_id: str) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            ag = await admin.agreements.get_by(agreement_id=agreement_id)
            if ag:
                await admin.agreements._session.delete(ag)
            return ActionStatusResponse(ok=True)

    # ── Forms (Models) ────────────────────────────────────────────────────────

    async def list_forms(self, city_slot: int | None = None, *, admin_id: int | None = None) -> FormsListResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            forms = await admin.forms.get_all_forms(city_slot=city_slot, admin_id=admin_id)
            return FormsListResponse(
                items=[
                    FormListItem(
                        code=f.code,
                        name=f.profile.name if f.profile else f.code,
                        age=int(f.profile.age or 0) if f.profile else 0,
                        city_slot=f.publication.city_slot if f.publication else 1,
                        is_visible=f.publication.is_visible if f.publication else True,
                        is_verified=f.publication.is_verified if f.publication else False,
                        has_medical_certificate=f.publication.has_medical_certificate if f.publication else False,
                        photos=[p.storage_key for p in getattr(f, "photos", [])],
                    )
                    for f in forms
                ]
            )

    async def get_form(self, code: str, *, admin_id: int | None = None) -> FormDetailResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            f = await admin.forms.get_form(code, admin_id=admin_id)
            p = f.profile
            pr = f.pricing
            pub = f.publication
            priv = getattr(f, "private_channel", None)
            return FormDetailResponse(
                id=f.id,
                code=f.code,
                name=p.name if p else "",
                age=int(p.age or 0) if p else 0,
                height=int(p.height or 0) if p else 0,
                bust_size=int(p.bust_size or 0) if p else 0,
                caption=getattr(p, "caption", None) if p else None,
                one_hour_price=pr.one_hour_price if pr else None,
                two_hour_price=pr.two_hour_price if pr else None,
                three_hour_price=pr.three_hour_price if pr else None,
                overnight_price=pr.overnight_price if pr else None,
                city_slot=pub.city_slot if pub else 1,
                is_visible=pub.is_visible if pub else True,
                is_verified=pub.is_verified if pub else False,
                has_medical_certificate=pub.has_medical_certificate if pub else False,
                public_channel_url=pub.public_channel_url if pub else None,
                photos=[p.storage_key for p in getattr(f, "photos", [])],
                rating=float(f.rating or 0.0),
                orders_count=int(f.orders_count or 0),
                has_private_channel=bool(priv and priv.is_enabled),
                private_channel_url=priv.channel_url if priv else None,
                private_channel_price=priv.subscription_price if priv else None,
                private_channel_period=priv.subscription_period_days if priv else None,
            )

    async def create_form(
        self,
        form_data: dict[str, Any],
        files: list[tuple] | None = None,
        *,
        admin_id: int | None = None,
    ) -> FormDetailResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            f = await admin.forms.create_form(form_data, admin_id=admin_id)
            return await self.get_form(f.code, admin_id=admin_id)

    async def update_form(self, code: str, payload: dict[str, Any], *, admin_id: int | None = None) -> FormDetailResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.get_form(code, admin_id=admin_id)
            await admin.forms.update_form(code, payload)
            return await self.get_form(code, admin_id=admin_id)

    async def delete_form(self, code: str, *, admin_id: int | None = None) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.get_form(code, admin_id=admin_id)
            await admin.forms.delete_form(code)
            return ActionStatusResponse(ok=True)

    async def toggle_form_field(self, code: str, field: str, *, admin_id: int | None = None) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.get_form(code, admin_id=admin_id)
            await admin.forms.toggle_field(code, field)
            return ActionStatusResponse(ok=True)

    async def swap_positions(self, code_a: str, code_b: str, *, admin_id: int | None = None) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.get_form(code_a, admin_id=admin_id)
            await admin.forms.get_form(code_b, admin_id=admin_id)
            await admin.forms.swap_positions(code_a, code_b)
            return ActionStatusResponse(ok=True)

    async def add_form_photos(self, code: str, files: list[tuple]) -> ActionStatusResponse:
        return ActionStatusResponse(ok=True)

    async def delete_form_photo(self, code: str, index: int, *, admin_id: int | None = None) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.get_form(code, admin_id=admin_id)
            await admin.forms.delete_photo(code, index)
            return ActionStatusResponse(ok=True)

    # ── Reviews ───────────────────────────────────────────────────────────────

    async def list_reviews(self, code: str) -> ReviewsListResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            reviews = await admin.forms.get_reviews(code)
            return ReviewsListResponse(
                items=[
                    ReviewItem(
                        id=r.id,
                        author=r.author,
                        review_date=str(r.review_date) if r.review_date else None,
                        body=r.body,
                        score=int(r.score or 0),
                    )
                    for r in reviews
                ]
            )

    async def create_review(self, code: str, payload: dict[str, Any]) -> ReviewItem:
        async with resolve_session() as session:
            admin = AdminService(session)
            r = await admin.forms.create_review(code, payload)
            return ReviewItem(
                id=r.id,
                author=r.author,
                review_date=str(r.review_date) if r.review_date else None,
                body=r.body,
                score=int(r.score or 0),
            )

    async def update_review(self, review_id: int, payload: dict[str, Any]) -> ReviewItem:
        return ReviewItem(id=review_id, score=0)

    async def delete_review(self, review_id: int) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.delete_review(review_id)
            return ActionStatusResponse(ok=True)

    # ── Services ──────────────────────────────────────────────────────────────

    async def list_services(self, code: str) -> ServicesListResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            services = await admin.forms.get_services(code)
            return ServicesListResponse(
                items=[
                    ServiceItem(
                        id=s.id,
                        name=s.name,
                        is_included=bool(s.is_included),
                        extra_price=s.extra_price,
                    )
                    for s in services
                ]
            )

    async def create_service(self, code: str, payload: dict[str, Any]) -> ServiceItem:
        async with resolve_session() as session:
            admin = AdminService(session)
            s = await admin.forms.create_service(code, payload)
            return ServiceItem(
                id=s.id,
                name=s.name,
                is_included=bool(s.is_included),
                extra_price=s.extra_price,
            )

    async def update_service(self, service_id: int, payload: dict[str, Any]) -> ServiceItem:
        return ServiceItem(id=service_id, name="", is_included=False)

    async def delete_service(self, service_id: int) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.delete_service(service_id)
            return ActionStatusResponse(ok=True)

    # ── Additionals ───────────────────────────────────────────────────────────

    async def list_additionals(self, code: str) -> AdditionalsListResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            adds = await admin.forms.get_additionals(code)
            return AdditionalsListResponse(
                items=[
                    AdditionalItem(
                        id=a.id,
                        name=a.name,
                        price=int(a.price or 0),
                        is_available=bool(a.is_available),
                    )
                    for a in adds
                ]
            )

    async def create_additional(self, code: str, payload: dict[str, Any]) -> AdditionalItem:
        async with resolve_session() as session:
            admin = AdminService(session)
            a = await admin.forms.create_additional(code, payload)
            return AdditionalItem(
                id=a.id,
                name=a.name,
                price=int(a.price or 0),
                is_available=bool(a.is_available),
            )

    async def update_additional(self, additional_id: int, payload: dict[str, Any]) -> AdditionalItem:
        return AdditionalItem(id=additional_id, name="", price=0, is_available=True)

    async def delete_additional(self, additional_id: int) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.forms.delete_additional(additional_id)
            return ActionStatusResponse(ok=True)

    # ── Promos ────────────────────────────────────────────────────────────────

    async def list_promos(self, *, admin_id: int | None = None) -> PromosListResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            promos = await admin.list_promos(admin_id=admin_id)
            return PromosListResponse(
                items=[
                    PromoItem(
                        id=p.id,
                        name=p.code,
                        discount=int(p.discount_amount or 0),
                        created_at=p.created_at,
                    )
                    for p in promos
                ]
            )

    async def create_promo(self, payload: dict[str, Any], *, admin_id: int | None = None) -> PromoItem:
        async with resolve_session() as session:
            admin = AdminService(session)
            code = payload.get("name") or payload.get("code")
            discount = payload.get("discount") or payload.get("discount_amount") or 0
            p = await admin.create_promo(code=code, discount_amount=discount, admin_id=admin_id)
            return PromoItem(id=p.id, name=p.code, discount=int(p.discount_amount or 0), created_at=p.created_at)

    async def delete_promo(self, name: str, *, admin_id: int | None = None) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.promos.delete_by_name(name, admin_id=admin_id)
            return ActionStatusResponse(ok=True)

    # ── Cards ─────────────────────────────────────────────────────────────────

    async def list_cards(self) -> CardsListResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            cards = await admin.list_cards()
            return CardsListResponse(
                items=[
                    CardItem(
                        id=c.id,
                        card_number=c.card_number,
                        min_amount=c.min_amount,
                        max_amount=c.max_amount,
                        is_active=bool(c.is_active),
                    )
                    for c in cards
                ]
            )

    async def create_card(self, payload: dict[str, Any]) -> CardItem:
        async with resolve_session() as session:
            admin = AdminService(session)
            c = await admin.create_card(
                card_number=payload["card_number"],
                min_amount=payload["min_amount"],
                max_amount=payload["max_amount"],
            )
            return CardItem(
                id=c.id,
                card_number=c.card_number,
                min_amount=c.min_amount,
                max_amount=c.max_amount,
                is_active=bool(c.is_active),
            )

    async def toggle_card(self, card_id: int) -> CardItem:
        async with resolve_session() as session:
            admin = AdminService(session)
            c = await admin.toggle_card(card_id)
            if not c:
                raise ApiNotFoundError(f"Card not found: {card_id}")
            return CardItem(
                id=c.id,
                card_number=c.card_number,
                min_amount=c.min_amount,
                max_amount=c.max_amount,
                is_active=bool(c.is_active),
            )

    async def delete_card(self, card_id: int) -> ActionStatusResponse:
        async with resolve_session() as session:
            admin = AdminService(session)
            await admin.delete_card(card_id)
            return ActionStatusResponse(ok=True)


    # ── Admin Settings (Client Logs DM) ──────────────────────────────────────

    _client_log_settings_cache: dict[int, dict[str, bool]] = {}

    @staticmethod
    def _normalize_client_log_settings(raw_settings: dict | None) -> dict[str, bool]:
        from .schemas import CLIENT_LOG_SETTING_KEYS

        client_logs = (raw_settings or {}).get("client_logs") or {}
        return {key: bool(client_logs.get(key, True)) for key in CLIENT_LOG_SETTING_KEYS}

    async def get_client_log_settings(self, telegram_id: int) -> dict[str, bool]:
        cached = self._client_log_settings_cache.get(telegram_id)
        if cached is not None:
            return dict(cached)

        async with resolve_session() as session:
            admin = AdminService(session)
            adm = await admin.admins.get_by_telegram_id(telegram_id)
            normalized = self._normalize_client_log_settings(getattr(adm, "settings", None) if adm else None)
            self._client_log_settings_cache[telegram_id] = normalized
            return dict(normalized)

    async def toggle_client_log_setting(self, telegram_id: int, setting_key: str) -> dict[str, bool]:
        from .schemas import CLIENT_LOG_SETTING_KEYS

        if setting_key not in CLIENT_LOG_SETTING_KEYS:
            raise ValueError(f"Unknown client log setting key: {setting_key}")

        async with resolve_session() as session:
            admin = AdminService(session)
            adm, _ = await admin.admins.get_or_create(telegram_id)
            current_settings = dict(getattr(adm, "settings", None) or {})
            client_logs = dict(current_settings.get("client_logs") or {})
            client_logs[setting_key] = not bool(client_logs.get(setting_key, True))
            current_settings["client_logs"] = client_logs
            adm.settings = current_settings
            await session.flush()
            normalized = self._normalize_client_log_settings(current_settings)
            self._client_log_settings_cache[telegram_id] = normalized
            return dict(normalized)

    async def is_client_log_enabled(self, telegram_id: int, event_type: str) -> bool:
        from .schemas import CLIENT_LOG_EVENT_TO_KEY

        setting_key = CLIENT_LOG_EVENT_TO_KEY.get(event_type)
        if not setting_key:
            return True
        states = await self.get_client_log_settings(telegram_id)
        return bool(states.get(setting_key, True))
