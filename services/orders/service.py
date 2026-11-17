from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from services.exceptions import (
    AgreementNotAcceptedError,
    ClientBannedError,
    FormUnavailableError,
    OrderValidationError,
)
from repository.repositories.clients import ClientRepository
from repository.repositories.forms import FormRepository
from repository.repositories.orders import OrderRepository


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.orders = OrderRepository(session)
        self.clients = ClientRepository(session)
        self.forms = FormRepository(session)

    async def get_user_orders(self, user_id: int, status: str | None = None):
        return await self.orders.get_by_user(user_id, status=status)

    async def get_orders_paginated(
        self,
        user_id: int,
        query: str | None = None,
        page: int = 1,
        per_page: int = 10,
        status: str | None = None,
    ):
        return await self.orders.get_by_user_paginated(
            user_id=user_id,
            query=query,
            page=page,
            per_page=per_page,
            status=status,
        )

    async def get_order_by_number(self, order_number: str | int):
        return await self.orders.get_by_order_number(order_number)

    async def get_order_by_id(self, order_id: int):
        return await self.orders.get_by_id(order_id)

    async def create_order(
        self,
        *,
        user_id: int,
        form_code: str,
        duration_hours: int,
        address_id: int,
        scheduled_at: datetime | None = None,
    ):
        """
        Create a new order with business rule validation.

        Args:
            user_id: Client user ID
            form_code: Form code to book
            duration_hours: Duration in hours
            address_id: Address ID for service delivery
            scheduled_at: Optional scheduled time

        Returns:
            Created Order instance

        Raises:
            ClientBannedError: If client is banned
            AgreementNotAcceptedError: If client hasn't accepted agreement
            FormUnavailableError: If form is not available
            OrderValidationError: If validation fails
        """
        # Validate client
        client = await self.clients.get(user_id)
        if not client:
            raise OrderValidationError(f"Client {user_id} not found")

        if client.is_banned:
            raise ClientBannedError(user_id)

        if not client.has_accepted_agreement:
            raise AgreementNotAcceptedError(user_id)

        # Validate form
        form = await self.forms.get(form_code, include_pricing=True, include_publication=True)
        if not form:
            raise OrderValidationError(f"Form {form_code} not found")

        if not form.publication.is_visible:
            raise FormUnavailableError(form_code, "form is not visible")

        if not form.publication.is_verified:
            raise FormUnavailableError(form_code, "form is not verified")

        # Validate duration
        if duration_hours not in [1, 2, 3]:
            if duration_hours < 4:
                raise OrderValidationError(f"Invalid duration: {duration_hours} hours")

        # Calculate price based on duration
        if duration_hours == 1:
            price = form.pricing.one_hour_price
        elif duration_hours == 2:
            price = form.pricing.two_hour_price
        elif duration_hours == 3:
            price = form.pricing.three_hour_price
        else:
            price = form.pricing.overnight_price

        if price is None or price <= 0:
            raise OrderValidationError(f"Price not available for {duration_hours} hour(s)")

        # Apply discount if client has promo
        discount_amount = 0
        if client.promo_code:
            promo = await self._session.get(client.promo.__class__, client.promo_code)
            if promo:
                discount_amount = promo.discount_amount

        final_price = max(0, price - discount_amount)

        # Create order
        order = await self.orders.create(
            user_id=user_id,
            form_code=form_code,
            address_id=address_id,
            duration_hours=duration_hours,
            price=final_price,
            discount_amount=discount_amount,
            scheduled_at=scheduled_at,
            status="pending",
        )

        return order
