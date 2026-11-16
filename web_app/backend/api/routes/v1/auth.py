from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, status

from backend.assets.texts import t
from backend.auth import create_user_session_token
from backend.clients.api import api_client
from backend.core.settings import settings
from backend.schemas import CreateMockSessionRequest, CreateSessionRequest, WebAppSessionResponse
from backend.schemas.session import SessionClientData, SessionEnvironmentData, TelegramUserData

router = APIRouter(prefix="/web-app/api/v1/auth", tags=["web-app-auth"])
logger = logging.getLogger(__name__)


def _session_response(
    *,
    user_id: int,
    telegram_id: int,
    first_name: str | None,
    last_name: str | None,
    username: str | None,
    agreement_accepted: bool,
    is_mock: bool,
) -> WebAppSessionResponse:
    session_token, expires_at = create_user_session_token(
        user_id=user_id,
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        agreement_accepted=agreement_accepted,
        is_mock=is_mock,
    )
    return WebAppSessionResponse(
        session_token=session_token,
        expires_at=expires_at,
        user=TelegramUserData(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        ),
        client=SessionClientData(
            user_id=user_id,
            agreement_accepted=agreement_accepted,
            is_banned=False,
        ),
        environment=SessionEnvironmentData(telegram=not is_mock, mock=is_mock),
    )


@router.post("/session", response_model=WebAppSessionResponse)
async def create_session(payload: CreateSessionRequest) -> WebAppSessionResponse:
    init_data = str(payload.init_data or "").strip()
    logger.info(f"Creating session with init_data: {init_data[:100]}...")
    
    if not init_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error_invalid_init_data"))

    # Let the API validate init_data and bootstrap the client
    try:
        logger.info("Calling API bootstrap_client_with_init_data...")
        bootstrap = await api_client.client_v1.bootstrap_client_with_init_data(init_data=init_data)
        logger.info(f"Bootstrap successful: {bootstrap}")
    except Exception as exc:
        logger.error(f"Bootstrap failed: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error_invalid_init_data")) from exc

    return _session_response(
        user_id=bootstrap.client.user_id,
        telegram_id=bootstrap.user.user_id,
        first_name=bootstrap.user.first_name,
        last_name=bootstrap.user.last_name,
        username=bootstrap.user.username,
        agreement_accepted=bool(bootstrap.client.has_accepted_agreement),
        is_mock=False,
    )


@router.post("/mock-session", response_model=WebAppSessionResponse)
async def create_mock_session(payload: CreateMockSessionRequest) -> WebAppSessionResponse:
    if not settings.WEB_APP_ENABLE_MOCK_SESSION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error_mock_session_disabled"))
    bootstrap = await api_client.client_v1.bootstrap_client(
        user_id=payload.user.telegram_id,
        first_name=payload.user.first_name,
        last_name=payload.user.last_name,
        username=payload.user.username,
    )
    return _session_response(
        user_id=bootstrap.client.user_id,
        telegram_id=payload.user.telegram_id,
        first_name=payload.user.first_name,
        last_name=payload.user.last_name,
        username=payload.user.username,
        agreement_accepted=bool(bootstrap.client.has_accepted_agreement),
        is_mock=True,
    )
