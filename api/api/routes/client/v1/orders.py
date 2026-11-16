from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from models.orders import OrderStatus
from models.payments import TransactionType
from repositories.clients import ClientRepository
from repositories.forms import FormRepository
from repositories.orders import OrderRepository
from repositories.transactions import TransactionRepository
from schemas.client.common import ApiSchema

router = APIRouter(prefix="/orders", tags=["client-orders"])


class CreateOrderRequest(ApiSchema):
    user_id: int
    form_code: str | None = None
    form_snapshot: str | None = None
    city_name: str | None = None
    promo_code: str | None = None
    tariff_name: str | None = None
    additional_options: str | None = None
    scheduled_month: str | None = None
    scheduled_day: str | None = None
    scheduled_time: str | None = None
    meeting_place_type: str | None = None
    address_id: int | None = None


class OrderDetailResponse(ApiSchema):
    id: int
    order_number: str
    user_id: int
    status: str
    form_code: str | None = None
    form_snapshot: str | None = None
    city_name: str | None = None
    promo_code: str | None = None
    tariff_name: str | None = None
    additional_options: str | None = None
    scheduled_month: str | None = None
    scheduled_day: str | None = None
    scheduled_time: str | None = None
    meeting_place_type: str | None = None
    address_id: int | None = None
    created_at: datetime


@router.post("", response_model=OrderDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: CreateOrderRequest,
    session: AsyncSession = Depends(service_session),
) -> OrderDetailResponse:
    client_repo = ClientRepository(session)
    await client_repo.get_or_create(payload.user_id)

    order_repo = OrderRepository(session)
    order = await order_repo.create(
        user_id=payload.user_id,
        form_code=payload.form_code,
        form_snapshot=payload.form_snapshot,
        city_name=payload.city_name,
        promo_code=payload.promo_code,
        tariff_name=payload.tariff_name,
        additional_options=payload.additional_options,
        status=OrderStatus.PENDING,
        scheduled_month=payload.scheduled_month,
        scheduled_day=payload.scheduled_day,
        scheduled_time=payload.scheduled_time,
        meeting_place_type=payload.meeting_place_type,
        address_id=payload.address_id,
    )
    await session.commit()
    await session.refresh(order)

    return OrderDetailResponse(
        id=order.id,
        order_number=str(order.id),
        user_id=order.user_id,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        form_code=order.form_code,
        form_snapshot=order.form_snapshot,
        city_name=order.city_name,
        promo_code=order.promo_code,
        tariff_name=order.tariff_name,
        additional_options=order.additional_options,
        scheduled_month=order.scheduled_month,
        scheduled_day=order.scheduled_day,
        scheduled_time=order.scheduled_time,
        meeting_place_type=order.meeting_place_type,
        address_id=order.address_id,
        created_at=order.created_at,
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(service_session),
) -> OrderDetailResponse:
    order_repo = OrderRepository(session)
    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return OrderDetailResponse(
        id=order.id,
        order_number=str(order.id),
        user_id=order.user_id,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        form_code=order.form_code,
        form_snapshot=order.form_snapshot,
        city_name=order.city_name,
        promo_code=order.promo_code,
        tariff_name=order.tariff_name,
        additional_options=order.additional_options,
        scheduled_month=order.scheduled_month,
        scheduled_day=order.scheduled_day,
        scheduled_time=order.scheduled_time,
        meeting_place_type=order.meeting_place_type,
        address_id=order.address_id,
        created_at=order.created_at,
    )


class PayBalanceRequest(ApiSchema):
    user_id: int
    amount: int


class PayBalanceResponse(ApiSchema):
    ok: bool = True
    order_id: int
    balance: int
    status: str


@router.post("/{order_id}/pay-balance", response_model=PayBalanceResponse)
async def pay_order_balance(
    order_id: int,
    payload: PayBalanceRequest,
    session: AsyncSession = Depends(service_session),
) -> PayBalanceResponse:
    client_repo = ClientRepository(session)
    client = await client_repo.get(payload.user_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if int(getattr(client, "balance", 0) or 0) < payload.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

    order_repo = OrderRepository(session)
    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Deduct balance
    client.balance = int(getattr(client, "balance", 0) or 0) - payload.amount
    order.status = OrderStatus.COMPLETED

    # Increment model orders count if form exists
    if order.form_code:
        form_repo = FormRepository(session)
        form = await form_repo.get(order.form_code)
        if form:
            form.orders_count = (form.orders_count or 0) + 1

    # Create transaction
    tx_repo = TransactionRepository(session)
    await tx_repo.create_transaction(
        user_id=payload.user_id,
        amount=payload.amount,
        type=TransactionType.BALANCE_PAYMENT,
        status="completed",
        description=f"Оплата заказа #{order_id}",
        order_number=str(order_id),
        balance_after=client.balance,
    )

    await session.commit()
    await session.refresh(client)
    return PayBalanceResponse(
        ok=True,
        order_id=order_id,
        balance=client.balance,
        status="completed",
    )
