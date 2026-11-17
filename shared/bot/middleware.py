from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services import (
    AddressService,
    AdminService,
    CityService,
    ClientService,
    FormService,
    OrderService,
    PaymentService,
    SupportService,
)

current_session_var: ContextVar[AsyncSession | None] = ContextVar("current_session_var", default=None)


def get_current_session() -> AsyncSession | None:
    """Return the current AsyncSession from context, if available."""
    return current_session_var.get()


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware for aiogram:
    1. Creates a new AsyncSession on each event
    2. Instantiates domain services and injects them into the event handler kwargs
    3. Sets current session contextvar for any in-process service consumers
    4. Commits the session on success
    5. Rolls back on error
    6. Closes the session safely
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_maker() as session:
            token = current_session_var.set(session)
            # Inject session
            data["session"] = session

            # Inject domain services
            data["client_service"] = ClientService(session)
            data["clients_service"] = data["client_service"]  # alias
            data["form_service"] = FormService(session)
            data["forms_service"] = data["form_service"]  # alias
            data["order_service"] = OrderService(session)
            data["orders_service"] = data["order_service"]  # alias
            data["payment_service"] = PaymentService(session)
            data["payments_service"] = data["payment_service"]  # alias
            data["address_service"] = AddressService(session)
            data["addresses_service"] = data["address_service"]  # alias
            data["city_service"] = CityService(session)
            data["cities_service"] = data["city_service"]  # alias
            data["support_service"] = SupportService(session)
            data["admin_service"] = AdminService(session)

            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
            finally:
                current_session_var.reset(token)
