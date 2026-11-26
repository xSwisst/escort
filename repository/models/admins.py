from __future__ import annotations

from sqlalchemy import BigInteger, DateTime, Identity, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import Base
from shared.utils.time import now_msk


class Admin(Base):
    """Worker / Admin entity for referral attribution and multi-tenant isolation."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    settings: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=now_msk,
        server_default=func.now(),
        nullable=False,
    )

    clients: Mapped[list["Client"]] = relationship("Client", back_populates="admin")
    forms: Mapped[list["Form"]] = relationship("Form", back_populates="admin")
    promos: Mapped[list["Promo"]] = relationship("Promo", back_populates="admin")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="admin")
