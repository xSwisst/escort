from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from shared.utils.time import now_msk
from shared.db import Base


class Promo(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(Integer, Identity(), nullable=False, unique=True, index=True)
    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now())
    discount_amount: Mapped[int] = mapped_column(Integer, default=0)

    name = synonym("code")
    discount = synonym("discount_amount")

    admin: Mapped["Admin | None"] = relationship("Admin", back_populates="promos")
    clients: Mapped["list[Client]"] = relationship("Client", back_populates="promo")
