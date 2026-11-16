from __future__ import annotations

from core.settings import settings
from shared.http import ServiceClient

from .files import PhotosFilesApi


class ApiPhotosClient:
    def __init__(self) -> None:
        self._http = ServiceClient(
            settings.PHOTOS_API_URL or "http://photos:8005",
            settings.API_SECRET_KEY,
            service_name="api",
            target_audience="photos_service",
        )
        self.files = PhotosFilesApi(self._http)

    async def upload_file(self, content: bytes, content_type: str, token: str | None = None, file_name: str = "photo.jpg") -> dict:
        result = await self.files.upload_bytes(file_name=file_name, content=content, content_type=content_type)
        return {"file_name": result.file_name, "content_hash": result.content_hash, "path": result.path, "public_url": result.public_url}

    async def delete_file(self, file_name: str) -> dict:
        result = await self.files.delete(file_name)
        return {"ok": result.ok, "file_name": result.file_name}

    async def close(self) -> None:
        await self._http.close()


photos_client = ApiPhotosClient()
