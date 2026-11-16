"""Shared exceptions for API clients across all services."""


class ApiClientError(Exception):
    """Base exception for all API client errors."""
    pass


class ApiNotFoundError(ApiClientError):
    """Resource not found (404)."""
    pass


class ApiValidationError(ApiClientError):
    """Validation failed (422)."""
    pass


class ApiUnauthorizedError(ApiClientError):
    """Authentication failed (401)."""
    pass


class ApiForbiddenError(ApiClientError):
    """Authorization failed (403)."""
    pass
