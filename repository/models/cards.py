from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.utils.time import now_msk
from shared.db import Base


class Card(Base):
    """
    Банковские карты (реквизиты для оплаты).

    Содержит номер карты, лимиты по сумме (min/max),
    статус активности, признак мягкого удаления и информацию о создателе.
    """
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, autoincrement=True)
    card_number: Mapped[str] = mapped_column(String(64), nullable=False)
    min_amount: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    max_amount: Mapped[int] = mapped_column(BigInteger, default=1_000_000, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)
