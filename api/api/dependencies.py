from collections.abc import AsyncIterator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from core.settings import settings
from shared.auth import verify_token

_bearer = HTTPBearer(auto_error=False)


async def db_session() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


async def service_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        return verify_token(credentials.credentials, settings.API_SECRET_KEY, audience=settings.API_AUDIENCE)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token") from exc


async def service_session(
    _: dict = Depends(service_auth),
) -> AsyncIterator[AsyncSession]:
    async for session in db_session():
        yield session


async def admin_api_key_auth(
    api_key: str | None = Header(default=None, alias="X-API-Key"),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    """Verify authentication for admin endpoints: accepts service JWT token or X-API-Key"""
    # 1. Allow service-to-service JWT Bearer token (used by escort_admin_bot)
    if credentials is not None and credentials.scheme.lower() == "bearer":
        try:
            verify_token(credentials.credentials, settings.API_SECRET_KEY, audience=settings.API_AUDIENCE)
            return
        except Exception:
            pass

    # 2. Allow X-API-Key header (used by web admin panel / scripts)
    if api_key:
        if not settings.ADMIN_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ADMIN_API_KEY not configured",
            )
        if api_key == settings.ADMIN_API_KEY:
            return
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication: provide Bearer token or X-API-Key header",
    )


async def admin_session(
    _: None = Depends(admin_api_key_auth),
) -> AsyncIterator[AsyncSession]:
    """Database session for admin panel with API key or Bearer token auth"""
    async for session in db_session():
        yield session
