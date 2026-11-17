from __future__ import annotations

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.utils.time import now_msk
from shared.db import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(256), nullable=False)
    full_address: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now())

    client: Mapped["Client"] = relationship("Client", back_populates="addresses")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="address")

    @property
    def title(self) -> str:
        return self.label

    @title.setter
    def title(self, value: str) -> None:
        self.label = value

    @property
    def address(self) -> str:
        return self.full_address

    @address.setter
    def address(self, value: str) -> None:
        self.full_address = value
