from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.cards import Card
from repository.models.payments import PaymentInvoice
from repository.repositories.cards import CardRepository
from repository.repositories.clients import ClientRepository
from repository.repositories.invoices import InvoiceRepository
from repository.repositories.transactions import TransactionRepository


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.cards = CardRepository(session)
        self.invoices = InvoiceRepository(session)
        self.clients = ClientRepository(session)
        self.transactions = TransactionRepository(session)

    async def get_suitable_card(self, amount: int) -> Card | None:
        return await self.cards.get_suitable_card(amount)

    async def create_invoice(
        self,
        *,
        invoice_number: str,
        user_id: int,
        amount: int,
        purpose: str,
        payment_method: str = "card",
        order_id: int | None = None,
        order_number: str | None = None,
        form_code: str | None = None,
        requisites_snapshot: dict | None = None,
        comment: str | None = None,
    ) -> PaymentInvoice:
        await self.clients.get_or_create(user_id)
        return await self.invoices.create_invoice(
            invoice_number=invoice_number,
            user_id=user_id,
            amount=amount,
            purpose=purpose,
            payment_method=payment_method,
            order_id=order_id,
            order_number=order_number,
            form_code=form_code,
            requisites_snapshot=requisites_snapshot,
            comment=comment,
        )

    async def get_invoice(self, invoice_number: str) -> PaymentInvoice | None:
        return await self.invoices.get_by_invoice_number(invoice_number)

    async def list_transactions(self, user_id: int, page: int = 1, page_size: int = 10):
        return await self.transactions.list_by_user(user_id, page=page, page_size=page_size)

    async def get_transaction(self, transaction_id: int):
        return await self.transactions.get(transaction_id)
