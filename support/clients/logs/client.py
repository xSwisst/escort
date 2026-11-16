from __future__ import annotations

from core.settings import settings
from shared.logging import LogsClient

logs_client = LogsClient(
    base_url=settings.LOGS_API_URL,
    service_name="support",
    secret_key=settings.LOGS_SECRET_KEY,
    target_audience="escort_logs",
)
