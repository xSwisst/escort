from __future__ import annotations

from pathlib import Path

import httpx

from .base import PhotosSection
from .schemas import FileDeleteResponse, FileUploadResponse, HealthResponse


class PhotosFilesApi(PhotosSection):
    async def upload_bytes(
        self,
        *,
        file_name: str,
        content: bytes,
        content_type: str,
    ) -> FileUploadResponse:
        files = {
            "file": (file_name, content, content_type),
        }
        try:
            payload = await self._client.post("/internal/v1/files", files=files)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(FileUploadResponse, payload)

    async def upload_path(
        self,
        *,
        path: str,
        content_type: str,
    ) -> FileUploadResponse:
        file_path = Path(path)
        return await self.upload_bytes(
            file_name=file_path.name,
            content=file_path.read_bytes(),
            content_type=content_type,
        )

    async def delete(self, file_name: str) -> FileDeleteResponse:
        try:
            payload = await self._client.delete(f"/internal/v1/files/{file_name}")
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(FileDeleteResponse, payload)

    async def health(self) -> HealthResponse:
        try:
            payload = await self._client.get("/v1/health")
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(HealthResponse, payload)
