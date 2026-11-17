from typing import Sequence

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from repository.models.clients import Client
from repository.models.forms import Form, FormPublication
from repository.repositories.base import BaseRepository


class FormRepository(BaseRepository[Form]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Form)

    @staticmethod
    def _with_private_channel(statement):
        return statement.options(
            selectinload(Form.private_channel),
            selectinload(Form.photos),
        )

    async def get(
        self,
        pk,
        *,
        include_profile: bool = True,
        include_pricing: bool = True,
        include_publication: bool = True,
        include_private_channel: bool = True,
        include_photos: bool = True,
        include_reviews: bool = False,
        include_services: bool = False,
        include_additionals: bool = False,
    ) -> Form | None:
        """
        Get a form by code with optional eager loading of relationships.

        Args:
            pk: Form code
            include_profile: Load profile relationship (default True)
            include_pricing: Load pricing relationship (default True)
            include_publication: Load publication relationship (default True)
            include_private_channel: Load private_channel relationship
            include_photos: Load photos relationship
            include_reviews: Load reviews relationship
            include_services: Load services relationship
            include_additionals: Load additionals relationship

        Returns:
            Form instance or None
        """
        pk_str = str(pk).strip()
        if pk_str.isdigit():
            stmt = select(Form).where(or_(Form.code == pk_str, Form.id == int(pk_str)))
        else:
            stmt = select(Form).where(Form.code == pk_str)

        if include_profile:
            stmt = stmt.options(selectinload(Form.profile))
        if include_pricing:
            stmt = stmt.options(selectinload(Form.pricing))
        if include_publication:
            stmt = stmt.options(selectinload(Form.publication))
        if include_private_channel:
            stmt = stmt.options(selectinload(Form.private_channel))
        if include_photos:
            stmt = stmt.options(selectinload(Form.photos))
        if include_reviews:
            stmt = stmt.options(selectinload(Form.reviews))
        if include_services:
            stmt = stmt.options(selectinload(Form.services))
        if include_additionals:
            stmt = stmt.options(selectinload(Form.additionals))

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_visible_for_client(self, client: Client | None, *, active_city_slot: int | None = None) -> Sequence[Form]:
        if client is None:
            return []
        statement = (
            select(Form)
            .join(Form.publication)
            .where(FormPublication.is_visible.is_(True))
            .options(
                selectinload(Form.profile),
                selectinload(Form.pricing),
                selectinload(Form.publication),
                selectinload(Form.private_channel),
                selectinload(Form.photos),
            )
        )
        if active_city_slot is not None:
            statement = statement.where(FormPublication.city_slot == active_city_slot)
        statement = statement.order_by(FormPublication.sort_order.asc(), Form.created_at.asc())
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def get_all_admin(self, city_slot: int | None = None) -> Sequence[Form]:
        """Get all forms for admin panel with full relationships loaded"""
        stmt = (
            select(Form)
            .options(
                selectinload(Form.profile),
                selectinload(Form.pricing),
                selectinload(Form.publication),
                selectinload(Form.photos),
            )
            .order_by(Form.created_at.desc())
        )
        if city_slot is not None:
            stmt = stmt.join(Form.publication).where(FormPublication.city_slot == city_slot)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_form(
        self,
        code: str,
        profile_data: dict,
        pricing_data: dict,
        publication_data: dict,
    ) -> Form:
        """Create a new form with all related entities"""
        form = Form(code=code)
        self._session.add(form)
        await self._session.flush()

        # Import here to avoid circular imports
        from repository.models.forms import FormProfile, FormPricing, FormPublication

        clean_profile = dict(profile_data)
        if "caption" in clean_profile and "description" not in clean_profile:
            clean_profile["description"] = clean_profile.pop("caption")

        profile = FormProfile(form_code=code, **clean_profile)
        pricing = FormPricing(form_code=code, **pricing_data)
        publication = FormPublication(form_code=code, **publication_data)

        self._session.add(profile)
        self._session.add(pricing)
        self._session.add(publication)

        await self._session.flush()
        await self._session.refresh(form)
        return form

    async def update_form_profile(self, code: str, **fields) -> bool:
        """Update form profile fields"""
        from repository.models.forms import FormProfile

        clean_fields = dict(fields)
        if "caption" in clean_fields and "description" not in clean_fields:
            clean_fields["description"] = clean_fields.pop("caption")

        stmt = update(FormProfile).where(FormProfile.form_code == code).values(**clean_fields)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def update_form_pricing(self, code: str, **fields) -> bool:
        """Update form pricing fields"""
        from repository.models.forms import FormPricing

        stmt = update(FormPricing).where(FormPricing.form_code == code).values(**fields)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def update_form_publication(self, code: str, **fields) -> bool:
        """Update form publication fields"""
        from repository.models.forms import FormPublication

        stmt = update(FormPublication).where(FormPublication.form_code == code).values(**fields)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def delete_by_code(self, code: str) -> bool:
        """Delete form and all related entities (cascade)"""
        form = await self.get(code)
        if not form:
            return False
        await self._session.delete(form)
        await self._session.flush()
        return True

    async def swap_positions(self, code_a: str, code_b: str) -> bool:
        """Swap sort_order between two forms"""
        from repository.models.forms import FormPublication

        # Get both publications
        stmt = select(FormPublication).where(FormPublication.form_code.in_([code_a, code_b]))
        result = await self._session.execute(stmt)
        pubs = result.scalars().all()

        if len(pubs) != 2:
            return False

        pub_a = next((p for p in pubs if p.form_code == code_a), None)
        pub_b = next((p for p in pubs if p.form_code == code_b), None)

        if not pub_a or not pub_b:
            return False

        # Swap
        pub_a.sort_order, pub_b.sort_order = pub_b.sort_order, pub_a.sort_order
        await self._session.flush()
        return True
