from __future__ import annotations

import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from services.exceptions import FormNotFoundError
from repository.repositories.form_additionals import FormAdditionalRepository
from repository.repositories.form_photos import FormPhotoRepository
from repository.repositories.form_services import FormServiceRepository
from repository.repositories.forms import FormRepository
from repository.repositories.promos import PromoRepository
from repository.repositories.reviews import ReviewRepository


def _generate_form_code(length: int = 8) -> str:
    """Generate random form code"""
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class AdminFormService:
    """Service for admin form management operations"""

    def __init__(self, session: AsyncSession) -> None:
        self.forms = FormRepository(session)
        self.photos = FormPhotoRepository(session)
        self.reviews = ReviewRepository(session)
        self.services = FormServiceRepository(session)
        self.additionals = FormAdditionalRepository(session)
        self.promos = PromoRepository(session)
        self._session = session

    # ── Forms ─────────────────────────────────────────────────────────────

    async def get_all_forms(self, city_slot: int | None = None, *, admin_id: int | None = None):
        """Get all forms for admin panel"""
        return await self.forms.get_all_admin(city_slot=city_slot, admin_id=admin_id)

    async def get_form(self, code: str, *, admin_id: int | None = None):
        """Get form by code with all relationships"""
        form = await self.forms.get(
            code,
            include_profile=True,
            include_pricing=True,
            include_publication=True,
            include_photos=True,
        )
        if not form or (admin_id is not None and form.admin_id != admin_id):
            raise FormNotFoundError(code)
        return form

    async def create_form(self, data: dict, *, admin_id: int | None = None):
        """Create a new form with generated code"""
        # Generate unique code
        while True:
            code = _generate_form_code()
            existing = await self.forms.get(code)
            if not existing:
                break

        # Split data into related tables
        profile_data = {
            "name": data["name"],
            "age": data["age"],
            "height": data["height"],
            "bust_size": data["bust_size"],
            "caption": data.get("caption"),
        }

        pricing_data = {
            "one_hour_price": data.get("one_hour_price"),
            "two_hour_price": data.get("two_hour_price"),
            "three_hour_price": data.get("three_hour_price"),
            "overnight_price": data.get("overnight_price"),
        }

        publication_data = {
            "city_slot": data.get("city_slot", 1),
            "sort_order": data.get("sort_order", 0),
            "is_visible": data.get("is_visible", False),
            "is_verified": data.get("is_verified", False),
            "has_medical_certificate": data.get("has_medical_certificate", False),
        }

        form = await self.forms.create_form(
            code,
            profile_data,
            pricing_data,
            publication_data,
            admin_id=admin_id,
        )
        await self._session.commit()
        return form

    async def update_form(self, code: str, data: dict):
        """Update form fields"""
        form = await self.forms.get(code)
        if not form:
            raise FormNotFoundError(code)

        # Update root form fields (rating, orders)
        if "rating" in data and data["rating"] is not None:
            form.rating = float(data["rating"])
        if "orders" in data and data["orders"] is not None:
            form.orders_count = int(data["orders"])
        if "orders_count" in data and data["orders_count"] is not None:
            form.orders_count = int(data["orders_count"])

        # Update profile fields
        profile_fields = {}
        for field in ["name", "age", "height", "bust_size", "caption"]:
            if field in data and data[field] is not None:
                profile_fields[field] = data[field]
        if profile_fields:
            await self.forms.update_form_profile(code, **profile_fields)

        # Update pricing fields
        pricing_fields = {}
        for field in ["one_hour_price", "two_hour_price", "three_hour_price", "overnight_price"]:
            if field in data and data[field] is not None:
                pricing_fields[field] = data[field]
        if pricing_fields:
            await self.forms.update_form_pricing(code, **pricing_fields)

        # Update publication fields
        publication_fields = {}
        for field in ["city_slot", "sort_order", "is_visible", "is_verified", "has_medical_certificate", "public_channel_url"]:
            if field in data and data[field] is not None:
                publication_fields[field] = data[field]
        if publication_fields:
            await self.forms.update_form_publication(code, **publication_fields)

        await self._session.commit()
        return await self.get_form(code)

    async def delete_form(self, code: str) -> bool:
        """Delete form and all related data"""
        result = await self.forms.delete_by_code(code)
        if result:
            await self._session.commit()
        return result

    async def toggle_form_field(self, code: str, field: str) -> bool:
        """Toggle boolean field (is_visible, is_verified, has_medical_certificate)"""
        form = await self.forms.get(code, include_publication=True)
        if not form:
            raise FormNotFoundError(code)

        current_value = getattr(form.publication, field, None)
        if current_value is None:
            return False

        await self.forms.update_form_publication(code, **{field: not current_value})
        await self._session.commit()
        return True

    async def swap_positions(self, code_a: str, code_b: str) -> bool:
        """Swap sort_order between two forms"""
        result = await self.forms.swap_positions(code_a, code_b)
        if result:
            await self._session.commit()
        return result

    # ── Photos ────────────────────────────────────────────────────────────

    async def add_photos(self, code: str, urls: list[str]):
        """Add photos to form"""
        form = await self.forms.get(code)
        if not form:
            raise FormNotFoundError(code)

        photos = await self.photos.add_photos(code, urls)
        await self._session.commit()
        return photos

    async def delete_photo(self, code: str, index: int) -> bool:
        """Delete photo by index"""
        result = await self.photos.delete_by_index(code, index)
        if result:
            await self._session.commit()
        return result

    # ── Reviews ───────────────────────────────────────────────────────────

    async def get_reviews(self, code: str):
        """Get all reviews for a form"""
        return await self.reviews.get_by_form(code)

    async def create_review(self, code: str, data: dict):
        """Create a new review"""
        form = await self.forms.get(code)
        if not form:
            raise FormNotFoundError(code)

        review = await self.reviews.create_review(form_code=code, **data)
        await self._session.commit()
        return review

    async def update_review(self, review_id: int, data: dict):
        """Update review"""
        # Filter out None values
        update_data = {k: v for k, v in data.items() if v is not None}
        review = await self.reviews.update_review(review_id, **update_data)
        if review:
            await self._session.commit()
        return review

    async def delete_review(self, review_id: int) -> bool:
        """Delete review"""
        result = await self.reviews.delete_review(review_id)
        if result:
            await self._session.commit()
        return result

    # ── Services ──────────────────────────────────────────────────────────

    async def get_services(self, code: str):
        """Get all services for a form"""
        return await self.services.get_by_form(code)

    async def create_service(self, code: str, data: dict):
        """Create a new service"""
        form = await self.forms.get(code)
        if not form:
            raise FormNotFoundError(code)

        service = await self.services.create_service(form_code=code, **data)
        await self._session.commit()
        return service

    async def update_service(self, service_id: int, data: dict):
        """Update service"""
        service = await self.services.update_service(service_id, **data)
        if service:
            await self._session.commit()
        return service

    async def delete_service(self, service_id: int) -> bool:
        """Delete service"""
        result = await self.services.delete_service(service_id)
        if result:
            await self._session.commit()
        return result

    # ── Additionals ───────────────────────────────────────────────────────

    async def get_additionals(self, code: str):
        """Get all additional services for a form"""
        return await self.additionals.get_by_form(code)

    async def create_additional(self, code: str, data: dict):
        """Create a new additional service"""
        form = await self.forms.get(code)
        if not form:
            raise FormNotFoundError(code)

        additional = await self.additionals.create_additional(form_code=code, **data)
        await self._session.commit()
        return additional

    async def update_additional(self, additional_id: int, data: dict):
        """Update additional service"""
        # Filter out None values
        update_data = {k: v for k, v in data.items() if v is not None}
        additional = await self.additionals.update_additional(additional_id, **update_data)
        if additional:
            await self._session.commit()
        return additional

    async def delete_additional(self, additional_id: int) -> bool:
        """Delete additional service"""
        result = await self.additionals.delete_additional(additional_id)
        if result:
            await self._session.commit()
        return result

    # ── Promos ────────────────────────────────────────────────────────────

    async def get_all_promos(self):
        """Get all promos"""
        return await self.promos.get_all()

    async def create_promo(self, data: dict):
        """Create a new promo"""
        promo = await self.promos.create_promo(**data)
        await self._session.commit()
        return promo

    async def delete_promo(self, name: str) -> bool:
        """Delete promo by name"""
        result = await self.promos.delete_by_name(name)
        if result:
            await self._session.commit()
        return result


AdminFormsService = AdminFormService

__all__ = ["AdminFormService", "AdminFormsService"]
