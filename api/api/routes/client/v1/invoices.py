from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from repository.repositories.clients import ClientRepository
from repository.repositories.invoices import InvoiceRepository
from schemas.client.invoices import CreateInvoiceRequest, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["client-invoices"])


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: CreateInvoiceRequest,
    session: AsyncSession = Depends(service_session),
) -> InvoiceResponse:
    client_repo = ClientRepository(session)
    await client_repo.get_or_create(payload.user_id)

    invoice_repo = InvoiceRepository(session)
    invoice = await invoice_repo.create_invoice(
        invoice_number=payload.invoice_number,
        user_id=payload.user_id,
        amount=payload.amount,
        purpose=payload.purpose,
        payment_method=payload.payment_method,
        order_id=payload.order_id,
        order_number=payload.order_number,
        form_code=payload.form_code,
        requisites_snapshot=payload.requisites_snapshot,
        comment=payload.comment,
    )
    await session.commit()

    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        user_id=invoice.user_id,
        amount=invoice.amount,
        purpose=invoice.purpose.value if hasattr(invoice.purpose, "value") else str(invoice.purpose),
        status=invoice.status.value if hasattr(invoice.status, "value") else str(invoice.status),
        payment_method=invoice.payment_method,
        order_id=invoice.order_id,
        order_number=str(invoice.order_id) if invoice.order_id else None,
        form_code=invoice.form_code,
        requisites_snapshot=invoice.requisites_snapshot,
        comment=invoice.comment,
        created_at=invoice.created_at,
        paid_at=invoice.paid_at,
    )


@router.get("/{invoice_number}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_number: str,
    session: AsyncSession = Depends(service_session),
) -> InvoiceResponse:
    invoice_repo = InvoiceRepository(session)
    invoice = await invoice_repo.get_by_invoice_number(invoice_number)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        user_id=invoice.user_id,
        amount=invoice.amount,
        purpose=invoice.purpose.value if hasattr(invoice.purpose, "value") else str(invoice.purpose),
        status=invoice.status.value if hasattr(invoice.status, "value") else str(invoice.status),
        payment_method=invoice.payment_method,
        order_id=invoice.order_id,
        order_number=str(invoice.order_id) if invoice.order_id else None,
        form_code=invoice.form_code,
        requisites_snapshot=invoice.requisites_snapshot,
        comment=invoice.comment,
        created_at=invoice.created_at,
        paid_at=invoice.paid_at,
    )
