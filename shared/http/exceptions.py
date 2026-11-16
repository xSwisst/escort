"""
Shared exceptions for service-to-service communication.

These exceptions are used across all bot services (main, support, admin)
when communicating with the API service.
"""


class ServiceClientError(Exception):
    """Base exception for all service-to-service communication errors."""

    pass


class ServiceNotFoundError(ServiceClientError):
    """Raised when a resource is not found on the remote service."""

    pass


class ServiceAuthError(ServiceClientError):
    """Raised when service-to-service authentication fails."""

    pass


class ServiceTimeoutError(ServiceClientError):
    """Raised when a service-to-service request times out."""

    pass


class ServiceUnavailableError(ServiceClientError):
    """Raised when the remote service is unavailable."""

    pass
