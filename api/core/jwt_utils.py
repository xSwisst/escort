"""
JWT Token Utilities for Service-to-Service Authentication

This module provides functions to create JWT tokens for calling other services.
Each service has its own audience identifier.

Audiences:
- escort_api: Main API service
- photos_service: Photos service
- logs_service: Logs service
"""

import jwt
from datetime import datetime, timedelta


def create_service_token(
    secret_key: str,
    target_audience: str,
    issuer: str,
    ttl_minutes: int = 5,
) -> str:
    """
    Create a JWT token for calling another service.

    Args:
        secret_key: The API_SECRET_KEY shared across services
        target_audience: The audience of the target service (e.g., "escort_api", "photos_service")
        issuer: Who is creating the token (e.g., "main_bot", "escort_api")
        ttl_minutes: Token time-to-live in minutes (default: 5)

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_service_token(
        ...     secret_key=settings.API_SECRET_KEY,
        ...     target_audience="escort_api",
        ...     issuer="main_bot"
        ... )
        >>> # Use in HTTP request
        >>> headers = {"Authorization": f"Bearer {token}"}
    """
    now = datetime.utcnow()
    payload = {
        "sub": issuer,
        "aud": target_audience,
        "iat": now,
        "exp": now + timedelta(minutes=ttl_minutes),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")
