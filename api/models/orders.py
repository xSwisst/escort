import enum

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Identity, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.time_utils import now_msk
from shared.db import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, Identity(start=18245), primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now())
    form_code: Mapped[str | None] = mapped_column(String(64), ForeignKey("forms.code", ondelete="SET NULL"), nullable=True, index=True)
    form_snapshot: Mapped[str | None] = mapped_column(String(256), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    promo_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tariff_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    additional_options: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=32),
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
        nullable=False,
    )
    scheduled_month: Mapped[str | None] = mapped_column(String(16), nullable=True)
    scheduled_day: Mapped[str | None] = mapped_column(String(16), nullable=True)
    scheduled_time: Mapped[str | None] = mapped_column(String(16), nullable=True)
    meeting_place_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="orders")
    form: Mapped["Form | None"] = relationship("Form")
    address: Mapped["Address | None"] = relationship("Address", back_populates="orders")