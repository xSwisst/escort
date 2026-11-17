from __future__ import annotations

from typing import Any
from services.payments import PaymentService
from shared.bot.session import resolve_session
from .exceptions import ApiNotFoundError
from .schemas import InvoiceItem


class InvoicesApi:
    async def create_invoice(
        self,
        *,
        invoice_number: str,
        user_id: int,
        amount: int,
        purpose: str = "order",
        payment_method: str = "card",
        order_number: str | None = None,
        form_code: str | None = None,
        requisites_snapshot: str | None = None,
        comment: str | None = None,
    ) -> InvoiceItem:
        async with resolve_session() as session:
            ps = PaymentService(session)
            inv = await ps.create_invoice(
                invoice_number=invoice_number,
                user_id=user_id,
                amount=amount,
                purpose=purpose,
                payment_method=payment_method,
                order_number=order_number,
                form_code=form_code,
                requisites_snapshot={"card": requisites_snapshot} if requisites_snapshot else None,
                comment=comment,
            )
            return InvoiceItem(
                id=inv.id,
                invoice_number=inv.invoice_number,
                user_id=inv.user_id,
                amount=inv.amount,
                status=inv.status.value if hasattr(inv.status, "value") else str(inv.status),
                purpose=inv.purpose.value if hasattr(inv.purpose, "value") else str(inv.purpose),
                payment_method=inv.payment_method,
                order_number=inv.order_number,
                form_code=inv.form_code,
                requisites_snapshot=requisites_snapshot,
                created_at=inv.created_at,
            )

    async def get_invoice(self, invoice_number: str) -> InvoiceItem:
        async with resolve_session() as session:
            ps = PaymentService(session)
            inv = await ps.get_invoice(invoice_number)
            if not inv:
                raise ApiNotFoundError(f"Invoice not found: {invoice_number}")
            req_snap = None
            if inv.requisites_snapshot:
                req_snap = inv.requisites_snapshot.get("card") if isinstance(inv.requisites_snapshot, dict) else str(inv.requisites_snapshot)
            return InvoiceItem(
                id=inv.id,
                invoice_number=inv.invoice_number,
                user_id=inv.user_id,
                amount=inv.amount,
                status=inv.status.value if hasattr(inv.status, "value") else str(inv.status),
                purpose=inv.purpose.value if hasattr(inv.purpose, "value") else str(inv.purpose),
                payment_method=inv.payment_method,
                order_number=inv.order_number,
                form_code=inv.form_code,
                requisites_snapshot=req_snap,
                created_at=inv.created_at,
            )
