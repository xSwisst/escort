from __future__ import annotations

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from shared.http import ServiceClient

from .exceptions import ApiClientError, ApiNotFoundError

T = TypeVar("T", bound=BaseModel)


class ApiSection:
    def __init__(self, client: ServiceClient) -> None:
        self._client = client

    @staticmethod
    def _parse(model: type[T], payload: Any) -> T:
        return model.model_validate(payload)

    @staticmethod
    def _translate_error(exc: httpx.HTTPStatusError) -> None:
        if exc.response.status_code == 404:
            raise ApiNotFoundError(str(exc)) from exc
        raise ApiClientError(str(exc)) from exc

    async def _get(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        try:
            payload = await self._client.get(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)

    async def _post(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        try:
            payload = await self._client.post(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)

    async def _patch(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        try:
            payload = await self._client.patch(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)

    async def _delete(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        try:
            payload = await self._client.delete(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            self._translate_error(exc)
        return self._parse(model, payload)
