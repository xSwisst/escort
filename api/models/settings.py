from __future__ import annotations

from sqlalchemy import DateTime, Identity, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.time_utils import now_msk
from models.promos import Promo
from shared.db import Base


class Agreement(Base):
    __tablename__ = "agreements"

    id: Mapped[int] = mapped_column(Integer, Identity(), nullable=False, unique=True, index=True)
    agreement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now())
    document_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    clients: Mapped[list["Client"]] = relationship("Client", back_populates="agreement")


__all__ = ["Agreement", "Promo"]
