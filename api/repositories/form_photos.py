from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.forms import FormPhoto
from repositories.base import BaseRepository


class FormPhotoRepository(BaseRepository[FormPhoto]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FormPhoto)

    async def get_by_form(self, form_code: str) -> list[FormPhoto]:
        """Get all photos for a form, ordered by sort_order"""
        result = await self._session.execute(
            select(FormPhoto)
            .where(FormPhoto.form_code == form_code)
            .order_by(FormPhoto.sort_order.asc(), FormPhoto.id.asc())
        )
        return list(result.scalars().all())

    async def add_photos(self, form_code: str, storage_keys: list[str]) -> list[FormPhoto]:
        """Add multiple photos to a form, ignoring duplicates"""
        if not storage_keys:
            return []

        # Get current max sort_order and existing storage keys
        existing = await self.get_by_form(form_code)
        existing_keys = {p.storage_key for p in existing}
        max_order = max([p.sort_order for p in existing], default=-1)

        # Deduplicate incoming keys while preserving order and filtering existing keys
        unique_keys = []
        seen = set(existing_keys)
        for key in storage_keys:
            if key and key not in seen:
                seen.add(key)
                unique_keys.append(key)

        photos = []
        for i, key in enumerate(unique_keys):
            photo = FormPhoto(
                form_code=form_code,
                storage_key=key,
                sort_order=max_order + i + 1,
            )
            self._session.add(photo)
            photos.append(photo)

        if photos:
            await self._session.flush()
            for photo in photos:
                await self._session.refresh(photo)
        return photos

    async def delete_by_index(self, form_code: str, index: int) -> bool:
        """Delete photo by its position index (0-based)"""
        photos = await self.get_by_form(form_code)
        if index < 0 or index >= len(photos):
            return False

        photo_to_delete = photos[index]
        await self._session.delete(photo_to_delete)
        await self._session.flush()
        return True

    async def delete_all_by_form(self, form_code: str) -> int:
        """Delete all photos for a form"""
        result = await self._session.execute(
            delete(FormPhoto).where(FormPhoto.form_code == form_code)
        )
        await self._session.flush()
        return result.rowcount
