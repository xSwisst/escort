"""
Модель LogThread для хранения связей с тредами форума Telegram.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from shared.db import Base


class LogThreadType(str, enum.Enum):
    """Типы тредов для логов"""

    CLIENT_REGISTRATION = "client_registration"
    CLIENT_AGREEMENT = "client_agreement"
    CLIENT_CITIES = "client_cities"
    CLIENT_ADDRESSES = "client_addresses"
    CLIENT_SUPPORT_SECTION = "client_support_section"
    CLIENT_SUPPORT_MESSAGES = "client_support_messages"
    PAYMENT_REQUESTS = "payment_requests"
    PAYMENT_CHECKS = "payment_checks"
    ORDERS = "orders"
    FORMS_VIEWS = "forms_views"
    FORMS_MANAGEMENT = "forms_management"
    PROMOCODE_CREATED = "promocode_created"
    PROMOCODE_ACTIVATED = "promocode_activated"
    REVIEWS = "reviews"
    MAILING = "mailing"


class LogThread(Base):
    """
    Таблица для хранения связей с тредами форума.

    При холодном старте или очистке форума, logs сервис создает все треды
    и сохраняет их ID в этой таблице для дальнейшего использования.
    """

    __tablename__ = "log_threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_type: Mapped[str] = mapped_column(
        Enum(LogThreadType, native_enum=False, length=50),
        unique=True,
        nullable=False,
        index=True,
    )
    thread_id: Mapped[int] = mapped_column(Integer, nullable=False)
    thread_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<LogThread(type={self.thread_type}, id={self.thread_id}, name={self.thread_name})>"
