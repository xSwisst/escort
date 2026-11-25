from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from services.exceptions import FormNotFoundError, FormUnavailableError
from repository.repositories.favorites import FavoriteRepository
from repository.repositories.form_additionals import FormAdditionalRepository
from repository.repositories.form_services import FormServiceRepository
from repository.repositories.forms import FormRepository
from repository.repositories.reviews import ReviewRepository


@dataclass
class FormCard:
    code: str
    name: str
    age: int
    height: int
    bust_size: int
    one_hour_price: int | None
    two_hour_price: int | None
    three_hour_price: int | None
    overnight_price: int | None
    caption: str | None
    is_verified: bool
    has_medical_certificate: bool
    rating: float
    orders: int
    public_channel_url: str | None
    photos: list[str]
    is_favorite: bool
    has_reviews: bool
    has_services: bool
    has_additionals: bool
    has_private_channel: bool
    weight: int | None = None
    discount_amount: int | None = None


class FormService:
    def __init__(self, session: AsyncSession) -> None:
        self.forms = FormRepository(session)
        self.favorites = FavoriteRepository(session)
        self.reviews = ReviewRepository(session)
        self.additionals = FormAdditionalRepository(session)
        self.services = FormServiceRepository(session)

    async def get_form(
        self,
        form_code: str,
        *,
        include_profile: bool = True,
        include_pricing: bool = True,
        include_publication: bool = True,
        include_private_channel: bool = True,
        include_photos: bool = True,
    ):
        """Get a form by code, raising an exception if not found."""
        form = await self.forms.get(
            form_code,
            include_profile=include_profile,
            include_pricing=include_pricing,
            include_publication=include_publication,
            include_private_channel=include_private_channel,
            include_photos=include_photos,
        )
        if not form:
            raise FormNotFoundError(form_code)
        return form

    async def get_form_if_available(self, form_code: str):
        """
        Get a form if it's available for booking.

        Raises:
            FormNotFoundError: If form doesn't exist
            FormUnavailableError: If form is not visible or not verified
        """
        form = await self.forms.get(form_code, include_publication=True)
        if not form:
            raise FormNotFoundError(form_code)

        if not form.publication.is_visible:
            raise FormUnavailableError(form_code, "form is not visible")

        if not form.publication.is_verified:
            raise FormUnavailableError(form_code, "form is not verified")

        return form

    async def get_visible_forms(self, client, *, active_city_slot: int | None = None):
        return await self.forms.get_visible_for_client(client, active_city_slot=active_city_slot)

    async def get_reviews(self, form_code: str):
        return await self.reviews.get_by_form(form_code)

    async def get_additionals(self, form_code: str):
        return await self.additionals.get_by_form(form_code)

    async def get_services(self, form_code: str):
        return await self.services.get_by_form(form_code)

    async def is_favorite(self, user_id: int, form_code: str) -> bool:
        return await self.favorites.exists(user_id=user_id, form_code=form_code)

    async def toggle_favorite(self, user_id: int, form_code: str) -> bool:
        return await self.favorites.toggle(user_id, form_code)

    async def get_private_channel(self, form_code: str):
        form = await self.get_form(form_code, include_private_channel=True)
        return getattr(form, "private_channel", None)

    async def get_form_card(
        self,
        user_id: int,
        form_code: str,
        discount_amount: int | None = None,
        *,
        client_admin_id: int | None = None,
        enforce_admin: bool = False,
    ) -> FormCard | None:
        try:
            form = await self.get_form(form_code)
        except FormNotFoundError:
            return None

        if enforce_admin:
            is_static = bool(form.publication and getattr(form.publication, "is_static", False))
            if not is_static and (client_admin_id is None or form.admin_id != client_admin_id):
                return None

        reviews = await self.get_reviews(form_code)
        services = await self.get_services(form_code)
        additionals = await self.get_additionals(form_code)
        is_fav = await self.is_favorite(user_id, form_code)

        profile = form.profile
        pricing = form.pricing
        publication = form.publication
        private_channel = getattr(form, "private_channel", None)
        has_priv = bool(
            private_channel
            and getattr(private_channel, "is_enabled", False)
            and getattr(private_channel, "subscription_price", None)
        )
        photos = [str(p.storage_key).strip() for p in getattr(form, "photos", []) if str(p.storage_key).strip()]

        return FormCard(
            code=form.code,
            name=profile.name if profile else "",
            age=int(profile.age or 0) if profile else 0,
            height=int(profile.height or 0) if profile else 0,
            weight=int(profile.weight) if profile and profile.weight is not None else None,
            bust_size=int(profile.bust_size or 0) if profile else 0,
            one_hour_price=pricing.one_hour_price if pricing else None,
            two_hour_price=pricing.two_hour_price if pricing else None,
            three_hour_price=pricing.three_hour_price if pricing else None,
            overnight_price=pricing.overnight_price if pricing else None,
            caption=getattr(profile, "caption", getattr(profile, "description", None)) if profile else None,
            is_verified=bool(publication.is_verified) if publication else False,
            has_medical_certificate=bool(publication.has_medical_certificate) if publication else False,
            rating=float(form.rating or 0.0),
            orders=int(form.orders_count or 0),
            public_channel_url=publication.public_channel_url if publication else None,
            photos=photos,
            is_favorite=is_fav,
            has_reviews=bool(reviews),
            has_services=bool(services),
            has_additionals=bool(additionals),
            has_private_channel=has_priv,
            discount_amount=discount_amount,
        )
