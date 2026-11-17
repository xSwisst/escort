from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)


async def validate_city(city_name: str) -> str | None:
    """
    Validate city name using Open-Meteo Geocoding API.

    Args:
        city_name: City name to validate

    Returns:
        Normalized city name if found, None otherwise
    """
    normalized = str(city_name or "").strip()
    if not normalized:
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": normalized, "count": 1, "language": "ru"},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.warning("City validation API error: %s", exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error during city validation: %s", exc)
        return None

    results = data.get("results") or []
    if not results:
        return None

    return results[0].get("name") or None


class CityService:
    def __init__(self, session=None) -> None:
        self._session = session

    async def validate_city(self, city_name: str) -> str | None:
        return await validate_city(city_name)
