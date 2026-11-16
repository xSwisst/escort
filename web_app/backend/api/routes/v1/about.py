from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.dependencies import user_session_auth
from backend.clients.api import api_client
from backend.core.settings import settings
from backend.schemas import AboutResponse

router = APIRouter(prefix="/web-app/api/v1/about", tags=["web-app-about"])


@router.get("", response_model=AboutResponse)
async def get_about(session_payload: dict = Depends(user_session_auth)) -> AboutResponse:
    try:
        agreement = await api_client.client_v1.get_agreement(user_id=int(session_payload["user_id"]))
        agreement_url = agreement.document_url
    except Exception:
        agreement_url = None

    return AboutResponse(
        title=settings.WEB_APP_TITLE,
        agreement_url=agreement_url,
        api_url=settings.API_BASE_URL,
        info_channel=settings.WEB_APP_INFO_CHANNEL_URL,
        reviews_channel=settings.WEB_APP_REVIEWS_CHANNEL_URL,
        sections=["about", "models", "support", "profile"],
    )
