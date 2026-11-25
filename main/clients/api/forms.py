from __future__ import annotations

from services.clients.service import ClientService
from services.forms.service import FormService
from shared.bot.session import resolve_session
from .exceptions import ApiNotFoundError
from .schemas import (
    FavoriteToggleResponse,
    FormAdditionalItem,
    FormAdditionalsResponse,
    FormCard,
    FormListItem,
    FormPrivateChannelResponse,
    FormReviewsResponse,
    FormServiceItem,
    FormServicesResponse,
    FormsListResponse,
    ReviewItem,
)


class FormsApi:
    async def list_forms(self, *, user_id: int, active_city_slot: int | None = None) -> FormsListResponse:
        async with resolve_session() as session:
            cs = ClientService(session)
            fs = FormService(session)
            client = await cs.get_client(user_id)
            forms = await fs.get_visible_forms(client, active_city_slot=active_city_slot)
            return FormsListResponse(
                items=[
                    FormListItem(
                        code=f.code,
                        name=f.profile.name if f.profile else f.code,
                        age=int(f.profile.age or 0) if f.profile else 0,
                    )
                    for f in forms
                ]
            )

    async def get_form_card(self, *, user_id: int, form_code: str) -> FormCard:
        async with resolve_session() as session:
            cs = ClientService(session)
            fs = FormService(session)
            client = await cs.get_client(user_id)
            discount = await cs.get_discount_amount(user_id)
            card = await fs.get_form_card(
                user_id,
                form_code,
                discount_amount=discount,
                client_admin_id=getattr(client, "admin_id", None),
                enforce_admin=True,
            )
            if not card:
                raise ApiNotFoundError(f"Form not found: {form_code}")
            return FormCard(**card.__dict__)

    async def toggle_favorite(self, *, user_id: int, form_code: str) -> FavoriteToggleResponse:
        async with resolve_session() as session:
            fs = FormService(session)
            is_fav = await fs.toggle_favorite(user_id, form_code)
            return FavoriteToggleResponse(is_favorite=is_fav)

    async def get_reviews(self, form_code: str) -> FormReviewsResponse:
        async with resolve_session() as session:
            fs = FormService(session)
            form = await fs.get_form(form_code)
            reviews = await fs.get_reviews(form_code)
            return FormReviewsResponse(
                form_code=form_code,
                form_name=form.profile.name if form.profile else form_code,
                items=[
                    ReviewItem(
                        author=r.author,
                        review_date=str(r.review_date) if r.review_date else None,
                        body=r.body,
                        score=int(r.score or 0),
                    )
                    for r in reviews
                ],
            )

    async def get_additionals(self, form_code: str) -> FormAdditionalsResponse:
        async with resolve_session() as session:
            fs = FormService(session)
            form = await fs.get_form(form_code)
            additionals = await fs.get_additionals(form_code)
            return FormAdditionalsResponse(
                form_code=form_code,
                form_name=form.profile.name if form.profile else form_code,
                items=[
                    FormAdditionalItem(
                        name=a.name,
                        price=int(a.price or 0),
                        is_available=bool(a.is_available),
                    )
                    for a in additionals
                ],
            )

    async def get_services(self, form_code: str) -> FormServicesResponse:
        async with resolve_session() as session:
            fs = FormService(session)
            form = await fs.get_form(form_code)
            services = await fs.get_services(form_code)
            return FormServicesResponse(
                form_code=form_code,
                form_name=form.profile.name if form.profile else form_code,
                items=[
                    FormServiceItem(
                        id=s.id,
                        name=s.name,
                        is_included=bool(s.is_included),
                        extra_price=s.extra_price,
                    )
                    for s in services
                ],
            )

    async def get_private_channel(self, form_code: str) -> FormPrivateChannelResponse:
        async with resolve_session() as session:
            fs = FormService(session)
            priv = await fs.get_private_channel(form_code)
            if not priv:
                return FormPrivateChannelResponse(is_enabled=False)
            return FormPrivateChannelResponse(
                is_enabled=bool(priv.is_enabled),
                channel_url=priv.channel_url,
                subscription_price=priv.subscription_price,
                subscription_period_days=priv.subscription_period_days,
            )
