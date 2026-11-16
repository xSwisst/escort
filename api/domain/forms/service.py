from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import FormNotFoundError, FormUnavailableError
from repositories.favorites import FavoriteRepository
from repositories.form_additionals import FormAdditionalRepository
from repositories.form_services import FormServiceRepository
from repositories.forms import FormRepository
from repositories.reviews import ReviewRepository


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
