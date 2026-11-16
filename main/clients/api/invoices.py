from __future__ import annotations

from typing import Any

from .base import ApiSection
from .schemas import InvoiceItem


class InvoicesApi(ApiSection):
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
        payload: dict[str, Any] = {
            "invoice_number": invoice_number,
            "user_id": user_id,
            "amount": amount,
            "purpose": purpose,
            "payment_method": payment_method,
            "order_number": order_number,
            "form_code": form_code,
            "requisites_snapshot": requisites_snapshot,
            "comment": comment,
        }
        return await self._post("/client/v1/invoices", model=InvoiceItem, json=payload)

    async def get_invoice(self, invoice_number: str) -> InvoiceItem:
        return await self._get(f"/client/v1/invoices/{invoice_number}", model=InvoiceItem)
