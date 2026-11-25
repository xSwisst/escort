from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any, Awaitable, Callable, Dict
from urllib.parse import urlparse

import httpx
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User

from core.settings import settings
from shared.auth import create_service_token
from shared.utils.time import now_msk

logger = logging.getLogger(__name__)

_SYNC_INTERVAL = timedelta(days=1)
_PHOTO_FILE_RE = re.compile(r"^[a-f0-9]{64}\.(jpg|png|webp|gif)$")


def _extract_filename(url: str | None) -> str | None:
    if not url:
        return None
    name = urlparse(url.strip()).path.rsplit("/", 1)[-1]
    return name if _PHOTO_FILE_RE.fullmatch(name) else None


def _is_sync_due(synced_at: datetime | None, now: datetime) -> bool:
    if synced_at is None:
        return True
    if synced_at.tzinfo is None:
        synced_at = synced_at.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return (now - synced_at) >= _SYNC_INTERVAL


class ClientSyncMiddleware(BaseMiddleware):
    """
    Periodically (once per day) refreshes client profile fields (first_name,
    last_name, username) and compressed Telegram avatar in the photos service.
    """

    def __init__(self, *, photos_url: str | None = None, sync_interval: timedelta = _SYNC_INTERVAL) -> None:
        super().__init__()
        self._photos_url = (photos_url or settings.PHOTOS_API_URL or "http://photos:8005").rstrip("/")
        self._sync_interval = sync_interval
        self._http: httpx.AsyncClient | None = None

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=8.0)
        return self._http

    async def close(self) -> None:
        if self._http is not None and not self._http.is_closed:
            await self._http.aclose()
            self._http = None

    def _service_headers(self) -> dict[str, str]:
        secret = settings.PHOTOS_SECRET_KEY or settings.API_SECRET_KEY
        if not secret:
            return {}
        token = create_service_token(
            secret_key=secret,
            issuer="main",
            audience=settings.PHOTOS_AUDIENCE or "photos_service",
            ttl_hours=1,
        )
        return {"Authorization": f"Bearer {token}"}

    async def _upload_avatar(self, content: bytes) -> str | None:
        headers = self._service_headers()
        if not headers:
            return None
        resp = await self._get_http().post(
            f"{self._photos_url}/internal/v1/files",
            params={"category": "clients"},
            headers=headers,
            files={"file": ("avatar.jpg", content, "image/jpeg")},
        )
        if resp.status_code != 200:
            logger.warning("photos upload avatar returned status=%s", resp.status_code)
            return None
        payload = resp.json()
        return payload.get("public_url") or payload.get("path")

    async def _delete_avatar(self, old_url: str | None) -> None:
        fn = _extract_filename(old_url)
        headers = self._service_headers()
        if not fn or not headers:
            return
        try:
            await self._get_http().delete(
                f"{self._photos_url}/internal/v1/files/clients/{fn}",
                headers=headers,
            )
        except Exception:
            pass

    async def _fetch_tg_avatar(self, bot: Bot, user_id: int) -> bytes | None:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if not photos or not photos.photos or not photos.photos[0]:
            return None
        variants = photos.photos[0]
        target = next((p for p in variants if (p.width or 0) >= 256), variants[-1])
        buf = BytesIO()
        await bot.download(target, destination=buf)
        data = buf.getvalue()
        return data or None

    async def _sync_client(self, client: Any, tg_user: User, bot: Bot | None, session: Any) -> None:
        now = now_msk()
        if not _is_sync_due(getattr(client, "profile_synced_at", None), now):
            return

        client.first_name = tg_user.first_name
        client.last_name = tg_user.last_name
        client.username = tg_user.username

        if bot is not None:
            try:
                raw_avatar = await self._fetch_tg_avatar(bot, tg_user.id)
                if raw_avatar:
                    new_url = await self._upload_avatar(raw_avatar)
                    if new_url and new_url != client.avatar_url:
                        old_url = client.avatar_url
                        client.avatar_url = new_url
                        if old_url:
                            await self._delete_avatar(old_url)
                elif client.avatar_url is not None:
                    old_url = client.avatar_url
                    client.avatar_url = None
                    await self._delete_avatar(old_url)
            except Exception as exc:
                logger.warning("Failed to sync avatar for user_id=%s: %s", tg_user.id, exc)

        client.profile_synced_at = now
        await session.flush()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: User | None = getattr(event, "from_user", None)
        client_service = data.get("client_service")
        session = data.get("session")
        bot: Bot | None = data.get("bot")

        if tg_user is None or tg_user.is_bot or client_service is None or session is None:
            return await handler(event, data)

        client = await client_service.get_client(tg_user.id)
        if client is not None:
            await self._sync_client(client, tg_user, bot, session)
            return await handler(event, data)

        result = await handler(event, data)
        client = await client_service.get_client(tg_user.id)
        if client is not None:
            await self._sync_client(client, tg_user, bot, session)
        return result
