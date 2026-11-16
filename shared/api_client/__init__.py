"""Shared API client package."""

from .exceptions import (
    ApiClientError,
    ApiNotFoundError,
    ApiValidationError,
    ApiUnauthorizedError,
    ApiForbiddenError,
)

__all__ = [
    "ApiClientError",
    "ApiNotFoundError",
    "ApiValidationError",
    "ApiUnauthorizedError",
    "ApiForbiddenError",
]
