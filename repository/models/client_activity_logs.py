from __future__ import annotations

from typing import TYPE_CHECKING, Any
from sqlalchemy import BigInteger, DateTime, Identity, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship
from sqlalchemy.types import JSON

from shared.utils.time import now_msk
from shared.db import Base

if TYPE_CHECKING:
    from .clients import Client


class ClientActivityLog(Base):
    __tablename__ = "client_activity_logs"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )
    client_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=now_msk,
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    client: Mapped["Client"] = relationship(
        "Client",
        primaryjoin="foreign(ClientActivityLog.user_id) == Client.user_id",
        back_populates="activity_logs",
    )
