"""
Менеджер тредов (форум-топиков) Telegram для логов.

При запуске загружает сохранённые thread_id из файла,
создаёт недостающие топики через aiogram и сохраняет маппинг обратно.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from aiogram.exceptions import TelegramBadRequest

from core.settings import settings
from .bot import bot
from .event_mapping import LogThreadType

logger = logging.getLogger(__name__)

_THREADS_FILE = Path(__file__).parent.parent / "data" / "threads.json"


class ThreadManager:
    """Управление форум-топиками Telegram через aiogram."""

    THREAD_NAMES: dict[str, str] = {
        LogThreadType.CLIENT_REGISTRATION: "Новый клиент",
        LogThreadType.CLIENT_AGREEMENT: "Принятие соглашения",
        LogThreadType.CLIENT_CITIES: "Города клиентов",
        LogThreadType.CLIENT_ADDRESSES: "Адреса клиентов",
        LogThreadType.CLIENT_SUPPORT_SECTION: "Раздел поддержки",
        LogThreadType.CLIENT_SUPPORT_MESSAGES: "Сообщения в поддержку",
        LogThreadType.PAYMENT_REQUESTS: "Заявки на пополнение",
        LogThreadType.PAYMENT_CHECKS: "Чеки",
        LogThreadType.ORDERS: "Оформления",
        LogThreadType.FORMS_VIEWS: "Открытие анкет",
        LogThreadType.FORMS_MANAGEMENT: "Анкеты",
        LogThreadType.PROMOCODE_CREATED: "Создание промокодов",
        LogThreadType.PROMOCODE_ACTIVATED: "Активация промокодов",
        LogThreadType.REVIEWS: "Отзывы",
        LogThreadType.MAILING: "Рассылки",
    }

    def __init__(self) -> None:
        self._cache: dict[str, int] = {}

    # -- public ----------------------------------------------------------

    async def initialize(self) -> None:
        """Загрузить сохранённые thread_id, проверить живы ли они, создать недостающие топики."""
        try:
            self._load()

            # Проверяем существующие треды в Telegram: если тред удалён, очищаем из кеша
            dead_threads: list[str] = []
            for thread_type, thread_id in list(self._cache.items()):
                is_alive = await self._is_thread_alive(thread_id)
                if not is_alive:
                    logger.warning(
                        "Thread %d for '%s' was deleted in Telegram. Will recreate.",
                        thread_id,
                        thread_type,
                    )
                    dead_threads.append(thread_type)

            for thread_type in dead_threads:
                self._cache.pop(thread_type, None)

            created = 0
            for thread_type in self.THREAD_NAMES:
                if thread_type not in self._cache:
                    tid = await self._create_topic(thread_type)
                    if tid is not None:
                        created += 1

            if created or dead_threads:
                self._save()

            logger.info(
                "ThreadManager ready — %d topics active (%d loaded, %d created/recreated)",
                len(self._cache),
                len(self._cache) - created,
                created,
            )
        except Exception:
            logger.exception("Error during ThreadManager initialization. Continuing startup...")

    def get_thread_id(self, thread_type: str) -> int | None:
        """Вернуть thread_id из кеша или None."""
        return self._cache.get(thread_type)

    async def ensure_thread(self, thread_type: str) -> int | None:
        """Вернуть thread_id; если топик не существует — создать на лету."""
        tid = self._cache.get(thread_type)
        if tid is not None:
            return tid

        tid = await self._create_topic(thread_type)
        if tid is not None:
            self._save()
        return tid

    async def recreate_thread(self, thread_type: str) -> int | None:
        """Удалить старый thread_id из кеша/файла и создать топик заново."""
        logger.info("Recreating missing thread for '%s'...", thread_type)
        self._cache.pop(thread_type, None)
        self._save()
        tid = await self._create_topic(thread_type)
        if tid is not None:
            self._save()
            logger.info("Successfully recreated thread for '%s' → thread_id=%d", thread_type, tid)
        return tid

    # -- private ---------------------------------------------------------

    async def _is_thread_alive(self, thread_id: int) -> bool:
        """Проверяет, существует ли еще тред в Telegram, отправляя typing action."""
        try:
            await bot.send_chat_action(
                chat_id=settings.LOGS_CHAT_ID,
                action="typing",
                message_thread_id=thread_id,
            )
            return True
        except TelegramBadRequest as exc:
            if "thread not found" in str(exc).lower():
                return False
            # Любая другая ошибка (например, chat_id, rate_limit) не означает, что тред удален
            return True
        except Exception:
            return True

    def _load(self) -> None:
        if not _THREADS_FILE.exists():
            return
        try:
            self._cache = json.loads(_THREADS_FILE.read_text(encoding="utf-8"))
            logger.info("Loaded %d thread IDs from %s", len(self._cache), _THREADS_FILE)
        except Exception:
            logger.exception("Failed to read %s", _THREADS_FILE)

    def _save(self) -> None:
        _THREADS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _THREADS_FILE.write_text(
            json.dumps(self._cache, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    async def _create_topic(self, thread_type: str) -> int | None:
        name = self.THREAD_NAMES.get(thread_type, thread_type)
        try:
            topic = await bot.create_forum_topic(
                chat_id=settings.LOGS_CHAT_ID,
                name=name,
            )
            self._cache[thread_type] = topic.message_thread_id
            logger.info("Created forum topic '%s' → thread_id=%d", name, topic.message_thread_id)
            return topic.message_thread_id
        except Exception:
            logger.exception("Failed to create forum topic '%s'", name)
            return None


thread_manager = ThreadManager()
