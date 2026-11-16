"""Re-export shared API exceptions for backwards compatibility."""

from shared.api_client import ApiClientError, ApiNotFoundError

__all__ = ["ApiClientError", "ApiNotFoundError"]
