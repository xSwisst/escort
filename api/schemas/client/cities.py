from __future__ import annotations

from pydantic import Field

from schemas.client.common import ApiSchema


class ValidateCityRequest(ApiSchema):
    city_name: str = Field(min_length=1, max_length=100)


class ValidateCityResponse(ApiSchema):
    city_name: str | None = None
    is_valid: bool = False
