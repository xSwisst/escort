"""Shared aiogram Bot instance for the logs service."""
from __future__ import annotations

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from core.settings import settings

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
