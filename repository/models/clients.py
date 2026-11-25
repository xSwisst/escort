from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Identity, Integer, String, func
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from shared.utils.time import now_msk
from shared.db import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, Identity(), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    has_accepted_agreement: Mapped[bool] = mapped_column(Boolean, default=False)
    agreement_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("agreements.agreement_id", ondelete="SET NULL"),
        nullable=True,
    )
    primary_city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    secondary_city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    active_city_slot: Mapped[int] = mapped_column(Integer, default=1)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    registered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now())
    promo_code: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("promotions.code", ondelete="SET NULL"),
        nullable=True,
    )

    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="client")
    cities: Mapped[list["ClientCity"]] = relationship(
        "ClientCity",
        back_populates="client",
        cascade="all, delete-orphan",
        order_by="ClientCity.slot.asc()",
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="client")
    invoices: Mapped[list["PaymentInvoice"]] = relationship("PaymentInvoice", back_populates="client")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="client")
    favorite_forms: Mapped[list["FormFavorite"]] = relationship("FormFavorite", back_populates="client")
    support_thread: Mapped["SupportThread | None"] = relationship("SupportThread", back_populates="client", uselist=False)
    support_messages: Mapped[list["SupportMessage"]] = relationship("SupportMessage", back_populates="client")
    agreement: Mapped["Agreement | None"] = relationship("Agreement", back_populates="clients")
    promo: Mapped["Promo | None"] = relationship("Promo", back_populates="clients")
    admin: Mapped["Admin | None"] = relationship("Admin", back_populates="clients")
    activity_logs: Mapped[list["ClientActivityLog"]] = relationship(
        "ClientActivityLog",
        primaryjoin="Client.user_id == foreign(ClientActivityLog.user_id)",
        back_populates="client",
        cascade="all, delete-orphan",
    )

