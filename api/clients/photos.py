from __future__ import annotations

import httpx
from core.settings import settings
from core.jwt_utils import create_service_token


class PhotosClient:
    """Client for photos service API"""

    def __init__(self):
        self.base_url = settings.PHOTOS_API_URL
        self.timeout = 30.0

    def _create_token(self) -> str:
        """Create JWT token for photos service"""
        return create_service_token(
            secret_key=settings.API_SECRET_KEY,
            target_audience="photos_service",
            issuer="escort_api",
        )

    async def upload_file(self, file_content: bytes, content_type: str) -> dict:
        """
        Upload file to photos service.

        Args:
            file_content: File bytes
            content_type: MIME type (image/jpeg, image/png, etc)

        Returns:
            dict with file_name, content_hash, path, public_url

        Raises:
            httpx.HTTPError: If upload fails
        """
        token = self._create_token()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            files = {"file": ("photo", file_content, content_type)}
            response = await client.post(
                f"{self.base_url}/internal/v1/files",
                files=files,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            return response.json()

    async def delete_file(self, file_name: str) -> dict:
        """
        Delete file from photos service.

        Args:
            file_name: File name to delete

        Returns:
            dict with file_name

        Raises:
            httpx.HTTPError: If deletion fails
        """
        token = self._create_token()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/internal/v1/files/{file_name}",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            return response.json()


photos_client = PhotosClient()
