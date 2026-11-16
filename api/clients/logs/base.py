from __future__ import annotations

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from shared.http import ServiceClient

T = TypeVar("T", bound=BaseModel)


class LogsClientError(Exception):
    pass


class LogsSection:
    def __init__(self, client: ServiceClient) -> None:
        self._client = client

    @staticmethod
    def _parse(model: type[T], payload: Any) -> T:
        return model.model_validate(payload)

    async def _get(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        try:
            payload = await self._client.get(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            raise LogsClientError(str(exc)) from exc
        return self._parse(model, payload)

    async def _post(self, path: str, *, model: type[T], **kwargs: Any) -> T:
        try:
            payload = await self._client.post(path, **kwargs)
        except httpx.HTTPStatusError as exc:
            raise LogsClientError(str(exc)) from exc
        return self._parse(model, payload)
