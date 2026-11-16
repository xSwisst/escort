from __future__ import annotations

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from shared.http import ServiceClient

T = TypeVar("T", bound=BaseModel)


class PhotosClientError(Exception):
    pass


class PhotosNotFoundError(PhotosClientError):
    pass


class PhotosSection:
    def __init__(self, client: ServiceClient) -> None:
        self._client = client

    @staticmethod
    def _parse(model: type[T], payload: Any) -> T:
        return model.model_validate(payload)

    @staticmethod
    def _translate_error(exc: httpx.HTTPStatusError) -> None:
        if exc.response.status_code == 404:
            raise PhotosNotFoundError(str(exc)) from exc
        raise PhotosClientError(str(exc)) from exc
