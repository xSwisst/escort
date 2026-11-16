from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Identity, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.utils.time import now_msk
from shared.db import Base


class InvoicePurpose(str, enum.Enum):
    DEPOSIT = "deposit"
    ORDER = "order"
    PRIVATE_CHANNEL = "private_channel"


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"
    EXPIRED = "expired"
    REJECTED = "rejected"


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    BALANCE_PAYMENT = "balance_payment"
    DIRECT_PAYMENT = "direct_payment"
    ORDER_PAYMENT = "order_payment"
    REFUND = "refund"
    ADMIN_ADJUST = "admin_adjust"


class PaymentInvoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False, index=True)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    purpose: Mapped[InvoicePurpose] = mapped_column(
        Enum(InvoicePurpose, native_enum=False, length=32),
        default=InvoicePurpose.DEPOSIT,
        server_default=InvoicePurpose.DEPOSIT.value,
        nullable=False,
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, native_enum=False, length=32),
        default=InvoiceStatus.PENDING,
        server_default=InvoiceStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    payment_method: Mapped[str] = mapped_column(String(32), default="manual_card", server_default="manual_card")

    order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    form_code: Mapped[str | None] = mapped_column(String(64), ForeignKey("forms.code", ondelete="SET NULL"), nullable=True, index=True)

    requisites_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(String(256), nullable=True)
    confirmed_by_admin_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())
    paid_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="invoices")
    order: Mapped["Order | None"] = relationship("Order")
    form: Mapped["Form | None"] = relationship("Form")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="invoice")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True)

    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, native_enum=False, length=32),
        nullable=False,
        index=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    status: Mapped[str] = mapped_column(String(32), default="completed", server_default="completed")

    purpose: Mapped[str | None] = mapped_column(String(32), nullable=True)
    order_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str] = mapped_column(String(256), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())

    client: Mapped["Client"] = relationship("Client", back_populates="transactions")
    invoice: Mapped["PaymentInvoice | None"] = relationship("PaymentInvoice", back_populates="transactions")