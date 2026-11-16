"""Logs client instance для main сервиса"""
from __future__ import annotations

from core.settings import settings
from shared.logging import LogsClient

logs_client = LogsClient(base_url=settings.LOGS_API_URL)
