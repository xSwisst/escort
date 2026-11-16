"""
DEPRECATED: Use API endpoint instead.

New bots should call:
POST /client/v1/cities/validate
{
  "city_name": "Moscow"
}

This module is kept for backward compatibility only.
"""
import httpx

from core.settings import settings
from shared.auth import create_service_token


async def validate_city(city_name: str) -> str | None:
    """
    DEPRECATED: Use POST /client/v1/cities/validate instead.

    Validate city name via API service.
    """
    normalized = str(city_name or "").strip()
    if not normalized:
        return None

    try:
        token = create_service_token(
            secret_key=settings.API_SECRET_KEY,
            issuer="main",
            audience=settings.API_AUDIENCE,
            ttl_hours=1,
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.API_BASE_URL}/client/v1/cities/validate",
                json={"city_name": normalized},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("is_valid"):
                return data.get("city_name")
            return None

    except Exception:
        return None
