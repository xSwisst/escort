from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import Base
from shared.utils.time import now_msk


class City(Base):
    """Static cities directory for parsed forms."""

    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=now_msk,
        server_default=func.now(),
        nullable=False,
    )

    publications: Mapped[list["FormPublication"]] = relationship("FormPublication", back_populates="city")
    client_links: Mapped[list["ClientCity"]] = relationship("ClientCity", back_populates="city")


class ClientCity(Base):
    """Client-to-city link supporting slot 1 (worker forms) and slots 2+ (static parsed cities)."""

    __tablename__ = "client_cities"
    __table_args__ = (
        UniqueConstraint("client_id", "slot", name="uq_client_cities_client_slot"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clients.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    city_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("cities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    city_name: Mapped[str] = mapped_column(String(128), nullable=False)
    slot: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=now_msk,
        server_default=func.now(),
        nullable=False,
    )

    client: Mapped["Client"] = relationship("Client", back_populates="cities")
    city: Mapped["City | None"] = relationship("City", back_populates="client_links")
