from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import httpx

from core.settings import settings
from shared.auth import create_service_token

if TYPE_CHECKING:
    from schemas import LogEventRequest

logger = logging.getLogger(__name__)

CLIENT_ACTIVITY_EVENTS = {
    "new_user",
    "agreement_accepted",
    "add_city",
    "change_of_city",
    "add_address",
    "remove_address",
    "message_to_support",
    "open_support_section",
    "payment_request",
    "get_check_of_top_up",
    "get_check_of_payment_model",
    "get_check_of_payment_private_channel",
    "new_order",
    "open_model_form",
    "promocode_activated",
}


def _get_auth_headers() -> dict[str, str]:
    if not settings.API_SECRET_KEY:
        return {}
    token = create_service_token(
        secret_key=settings.API_SECRET_KEY,
        issuer=settings.API_AUDIENCE,
        audience=settings.API_TARGET_AUDIENCE,
        ttl_hours=1,
    )
    return {"Authorization": f"Bearer {token}"}


class ClientLogHistoryService:
    def is_activity_event(self, event_type: str) -> bool:
        return event_type in CLIENT_ACTIVITY_EVENTS

    async def record_activity(self, event: LogEventRequest) -> int | None:
        if not self.is_activity_event(event.event_type):
            return None

        payload = event.payload or {}
        raw_user_id = (
            payload.get("user_id")
            or payload.get("client_id")
            or payload.get("uid")
            or event.actor_id
            or event.chat_id
        )
        if not raw_user_id:
            return None

        try:
            user_id = int(raw_user_id)
        except (ValueError, TypeError):
            return None

        url = f"{settings.API_BASE_URL.rstrip('/')}/internal/v1/client-logs"
        body = {
            "user_id": user_id,
            "event_type": event.event_type,
            "payload": payload,
            "occurred_at": event.occurred_at.isoformat() if event.occurred_at else None,
        }

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(url, json=body, headers=_get_auth_headers())
                if resp.status_code in (200, 201):
                    data = resp.json()
                    return data.get("id")
                else:
                    logger.warning(
                        "Failed to record client activity log: status=%s, body=%s",
                        resp.status_code,
                        resp.text,
                    )
        except Exception as exc:
            logger.warning("Error recording client activity log to API: %s", exc)

        return None


client_log_history = ClientLogHistoryService()
