import jwt
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from core.settings import settings

security = HTTPBearer()


def verify_service_token(credentials=Depends(security)) -> dict:
    """
    Verify JWT token for service-to-service communication.
    Checks signature and audience.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.API_SECRET_KEY,
            algorithms=["HS256"],
            audience=settings.API_AUDIENCE,
        )
        return payload
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Token not for this service")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_admin_api_key(x_api_key: str = Header(...)) -> str:
    """
    Verify admin API key for admin endpoints.
    """
    if not settings.ADMIN_API_KEY:
        raise HTTPException(status_code=500, detail="Admin API key not configured")

    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    return x_api_key
