from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import service_auth
from schemas import LogEventRequest, LogEventResponse
from services.telegram import telegram_log_sender

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["logs-events"])


@router.post("", response_model=LogEventResponse)
async def create_event(
    payload: LogEventRequest,
    _: dict = Depends(service_auth),
) -> LogEventResponse:
    try:
        delivered = await telegram_log_sender.send(payload)
    except Exception:
        logger.exception("Failed to deliver log event for %s", payload.event_type)
        delivered = False
    return LogEventResponse(delivered=delivered, trace_id=payload.trace_id)
