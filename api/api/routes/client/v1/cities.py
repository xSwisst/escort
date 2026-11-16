from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from domain.cities import validate_city
from schemas.client.cities import ValidateCityRequest, ValidateCityResponse

router = APIRouter(prefix="/cities", tags=["cities"])


@router.post("/validate", response_model=ValidateCityResponse)
async def validate_city_endpoint(
    payload: ValidateCityRequest,
    session: AsyncSession = Depends(service_session),
) -> ValidateCityResponse:
    """
    Validate city name using geocoding API.

    Returns normalized city name if valid, or None if not found.
    """
    normalized_city = await validate_city(payload.city_name)

    return ValidateCityResponse(
        city_name=normalized_city,
        is_valid=normalized_city is not None,
    )
