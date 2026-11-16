from fastapi import APIRouter, Depends

from backend.api.dependencies import user_session_auth
from backend.core.settings import settings
from backend.schemas import SupportResponse

router = APIRouter(prefix="/web-app/api/v1/support", tags=["web-app-support"])


@router.get("", response_model=SupportResponse)
async def get_support(_: dict = Depends(user_session_auth)) -> SupportResponse:
    return SupportResponse(
        support_bot_url=settings.WEB_APP_SUPPORT_BOT_URL,
        info_channel=settings.WEB_APP_INFO_CHANNEL_URL,
        reviews_channel=settings.WEB_APP_REVIEWS_CHANNEL_URL,
    )
