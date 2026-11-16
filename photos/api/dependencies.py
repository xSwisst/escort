from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from assets.texts import t
from core.settings import settings
from shared.auth import verify_token

_bearer = HTTPBearer(auto_error=False)


async def service_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error_missing_bearer_token"))
    try:
        payload = verify_token(credentials.credentials, settings.API_SECRET_KEY, audience=settings.API_AUDIENCE)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error_invalid_bearer_token")) from exc

    issuer = str(payload.get("iss") or "").strip()
    if issuer not in settings.allowed_issuers:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error_service_issuer_not_allowed"))
    return payload
