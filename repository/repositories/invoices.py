from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.utils.time import now_msk
from repository.models.payments import InvoicePurpose, InvoiceStatus, PaymentInvoice
from repository.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[PaymentInvoice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PaymentInvoice)

    async def get_by_invoice_number(self, invoice_number: str) -> PaymentInvoice | None:
        stmt = select(PaymentInvoice).where(PaymentInvoice.invoice_number == invoice_number)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_invoice(
        self,
        *,
        invoice_number: str,
        user_id: int,
        amount: int,
        purpose: InvoicePurpose | str = InvoicePurpose.DEPOSIT,
        payment_method: str = "manual_card",
        order_id: int | None = None,
        order_number: str | int | None = None,
        form_code: str | None = None,
        requisites_snapshot: str | None = None,
        comment: str | None = None,
    ) -> PaymentInvoice:
        existing = await self.get_by_invoice_number(invoice_number)
        if existing:
            return existing

        if isinstance(purpose, str):
            try:
                purpose_val = InvoicePurpose(purpose)
            except ValueError:
                purpose_val = InvoicePurpose.DEPOSIT
        else:
            purpose_val = purpose

        resolved_order_id = order_id
        if resolved_order_id is None and order_number is not None:
            try:
                resolved_order_id = int(str(order_number).strip().lstrip("#"))
            except (ValueError, TypeError):
                resolved_order_id = None

        if resolved_order_id is not None:
            from repository.models.orders import Order
            order_exists = (await self._session.execute(
                select(Order.id).where(Order.id == resolved_order_id)
            )).scalar_one_or_none()
            if not order_exists:
                resolved_order_id = None

        invoice = PaymentInvoice(
            invoice_number=invoice_number,
            user_id=user_id,
            amount=amount,
            purpose=purpose_val,
            status=InvoiceStatus.PENDING,
            payment_method=payment_method,
            order_id=resolved_order_id,
            form_code=form_code,
            requisites_snapshot=requisites_snapshot,
            comment=comment,
        )
        self._session.add(invoice)
        await self._session.flush()
        return invoice

    async def approve_invoice(self, invoice_number: str, confirmed_by_admin_id: int | None = None) -> PaymentInvoice | None:
        invoice = await self.get_by_invoice_number(invoice_number)
        if not invoice:
            return None
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = now_msk()
        if confirmed_by_admin_id is not None:
            invoice.confirmed_by_admin_id = confirmed_by_admin_id
        await self._session.flush()
        return invoice

    async def reject_invoice(self, invoice_number: str) -> PaymentInvoice | None:
        invoice = await self.get_by_invoice_number(invoice_number)
        if not invoice:
            return None
        invoice.status = InvoiceStatus.REJECTED
        await self._session.flush()
        return invoice
