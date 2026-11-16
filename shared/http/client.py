from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from shared.auth import create_service_token


class ServiceClient:
    def __init__(
        self,
        base_url: str,
        secret_key: str,
        *,
        service_name: str,
        target_audience: str | None = None,
        timeout: float = 10.0,
        token_ttl_sec: int = 3600,
        token_refresh_leeway_sec: int = 60,
    ):
        self._base_url = base_url.rstrip("/")
        self._secret_key = secret_key
        self._service_name = service_name
        self._target_audience = target_audience
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._token_ttl_sec = max(60, token_ttl_sec)
        self._token_refresh_leeway_sec = max(0, token_refresh_leeway_sec)
        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._token_lock = asyncio.Lock()

    def _build_token(self) -> str:
        return create_service_token(
            self._secret_key,
            issuer=self._service_name,
            audience=self._target_audience,
            ttl_hours=max(1, self._token_ttl_sec // 3600),
        )

    async def _ensure_token(self) -> str:
        now = time.monotonic()
        if self._token and now < self._token_expires_at - self._token_refresh_leeway_sec:
            return self._token
        async with self._token_lock:
            now = time.monotonic()
            if self._token and now < self._token_expires_at - self._token_refresh_leeway_sec:
                return self._token
            self._token = self._build_token()
            self._token_expires_at = now + self._token_ttl_sec
            return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._ensure_token()
        return {"Authorization": f"Bearer {token}"}

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        client = self._ensure_client()
        headers = await self._headers()
        if "headers" in kwargs:
            extra_headers = kwargs.pop("headers")
            if isinstance(extra_headers, dict):
                headers.update(extra_headers)
        response = await client.request(method, path, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    async def get(self, path: str, **kwargs: Any) -> Any:
        response = await self._request("GET", path, **kwargs)
        return response.json()

    async def post(self, path: str, **kwargs: Any) -> Any:
        response = await self._request("POST", path, **kwargs)
        return response.json()

    async def patch(self, path: str, **kwargs: Any) -> Any:
        response = await self._request("PATCH", path, **kwargs)
        return response.json()

    async def put(self, path: str, **kwargs: Any) -> Any:
        response = await self._request("PUT", path, **kwargs)
        return response.json()

    async def delete(self, path: str, **kwargs: Any) -> Any:
        response = await self._request("DELETE", path, **kwargs)
        return response.json()
