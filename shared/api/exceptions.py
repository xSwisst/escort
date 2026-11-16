"""
Shared exceptions for API client communication.

These exceptions are used by service-to-service API clients
(main, support, admin, web_app) when communicating with the API service.
"""


class ApiClientError(Exception):
    """Base exception for API client errors."""

    pass


class ApiNotFoundError(ApiClientError):
    """Raised when a requested resource is not found (404)."""

    pass


class ApiValidationError(ApiClientError):
    """Raised when request validation fails (422)."""

    pass


class ApiAuthenticationError(ApiClientError):
    """Raised when authentication fails (401)."""

    pass


class ApiServerError(ApiClientError):
    """Raised when the API returns a server error (5xx)."""

    pass
