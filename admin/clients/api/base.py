from __future__ import annotations

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from core.settings import settings
from shared.http import ServiceClient

from .exceptions import ApiClientError, ApiNotFoundError

T = TypeVar("T", bound=BaseModel)


class ApiSection:
    def __init__(self, client: ServiceClient) -> None:
        self._client = client

    @staticmethod
    def _parse(model: type[T], payload: Any) -> T:
        if model is dict or model is Any or not hasattr(model, "model_validate"):
            return payload
        return model.model_validate(payload)

    @staticmethod
    def _translate_error(exc: httpx.HTTPStatusError) -> None:
        detail = ""
        try:
            detail = f" - {exc.response.text}"
        except Exception:
            pass
        if exc.response.status_code == 404:
            raise ApiNotFoundError(f"{exc}{detail}") from exc
        raise ApiClientError(f"{exc}{detail}") from exc

    def _inject_admin_headers(self, kwargs: dict[str, Any]) -> None:
        if settings.ADMIN_API_KEY:
            headers = kwargs.setdefault("headers", {})
            headers.setdefault("X-API-Key", settings.ADMIN_API_KEY)

    async def _get(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        self._inject_admin_headers(kwargs)
        try:
            payload = await self._client.get(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)

    async def _post(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        self._inject_admin_headers(kwargs)
        try:
            payload = await self._client.post(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)

    async def _put(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        self._inject_admin_headers(kwargs)
        try:
            payload = await self._client.put(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)

    async def _patch(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        self._inject_admin_headers(kwargs)
        try:
            payload = await self._client.patch(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)

    async def _delete(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        self._inject_admin_headers(kwargs)
        try:
            payload = await self._client.delete(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)
