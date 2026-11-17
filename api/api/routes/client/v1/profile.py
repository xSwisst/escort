from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from clients.logs import emit_client_log
from services.clients.service import ClientService
from repository.repositories.favorites import FavoriteRepository
from repository.repositories.orders import OrderRepository
from repository.repositories.transactions import TransactionRepository
from schemas.client import (
    FavoriteItem,
    FavoritesResponse,
    OrderItem,
    OrdersResponse,
    ProfileResponse,
    PromoActivateRequest,
    PromoActivateResponse,
    TransactionItem,
    TransactionsResponse,
)

router = APIRouter(prefix="/profile", tags=["client-profile"])


def _profile_city(client) -> str | None:
    active_city_slot = int(getattr(client, "active_city_slot", 1) or 1)
    if active_city_slot == 2 and getattr(client, "secondary_city", None):
        return client.secondary_city
    return getattr(client, "primary_city", None) or getattr(client, "secondary_city", None)


async def _get_client_or_404(session: AsyncSession, user_id: int):
    client = await ClientService(session).get_client(user_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


def _to_order_item(order) -> OrderItem:
    address_text = None
    if getattr(order, "address", None):
        address_text = f"{order.address.title}: {order.address.address}" if order.address.title else order.address.address
    return OrderItem(
        id=order.id,
        order_number=str(order.id),
        form_snapshot=order.form_snapshot,
        city_name=order.city_name,
        tariff_name=order.tariff_name,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        created_at=order.created_at,
        scheduled_month=order.scheduled_month,
        scheduled_day=order.scheduled_day,
        scheduled_time=order.scheduled_time,
        meeting_place_type=order.meeting_place_type,
        address_text=address_text,
    )


@router.get("", response_model=ProfileResponse)
async def profile_info(
    user_id: int = Query(...),
    session: AsyncSession = Depends(service_session),
) -> ProfileResponse:
    service = ClientService(session)
    client, _ = await service.get_or_create_client(user_id)
    return ProfileResponse(
        id=client.id,
        user_id=client.user_id,
        primary_city=client.primary_city,
        secondary_city=client.secondary_city,
        active_city_slot=int(client.active_city_slot or 1),
        city=_profile_city(client),
        rating=float(client.rating or 0.0),
        orders=await service.get_orders_count(user_id),
        balance=int(getattr(client, "balance", 0) or 0),
        promo=client.promo_code,
        registered_at=client.registered_at,
    )


@router.get("/orders", response_model=OrdersResponse)
async def profile_orders(
    user_id: int = Query(...),
    query: str | None = Query(default=None),
    status_filter: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(service_session),
) -> OrdersResponse:
    await _get_client_or_404(session, user_id)
    repo = OrderRepository(session)
    status_val = None
    if status_filter == "active":
        status_val = "pending"
    elif status_filter in {"completed", "rejected"}:
        status_val = status_filter

    orders, total = await repo.get_by_user_paginated(
        user_id=user_id,
        query=query,
        page=page,
        per_page=per_page,
        status=status_val,
    )
    items = [_to_order_item(order) for order in orders]
    return OrdersResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/orders/{order_number}", response_model=OrderItem)
async def profile_order_detail(
    order_number: str,
    user_id: int = Query(...),
    session: AsyncSession = Depends(service_session),
) -> OrderItem:
    await _get_client_or_404(session, user_id)
    repo = OrderRepository(session)
    order = await repo.get_by_order_number(order_number)
    if not order or order.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return _to_order_item(order)


@router.get("/transactions", response_model=TransactionsResponse)
async def profile_transactions(
    user_id: int = Query(...),
    query: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(service_session),
) -> TransactionsResponse:
    await _get_client_or_404(session, user_id)
    repo = TransactionRepository(session)
    txs, total = await repo.get_by_user_paginated(
        user_id=user_id,
        query=query,
        page=page,
        per_page=per_page,
    )
    items = [
        TransactionItem(
            id=tx.id,
            user_id=tx.user_id,
            invoice_id=tx.invoice_id,
            type=tx.type.value if hasattr(tx.type, "value") else str(tx.type),
            amount=tx.amount,
            balance_after=tx.balance_after,
            purpose=tx.purpose,
            order_number=tx.order_number,
            description=tx.description,
            created_at=tx.created_at,
        )
        for tx in txs
    ]
    return TransactionsResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/transactions/{transaction_id}", response_model=TransactionItem)
async def profile_transaction_detail(
    transaction_id: int,
    user_id: int = Query(...),
    session: AsyncSession = Depends(service_session),
) -> TransactionItem:
    await _get_client_or_404(session, user_id)
    repo = TransactionRepository(session)
    tx = await repo.get_by_id(transaction_id)
    if not tx or tx.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionItem(
        id=tx.id,
        user_id=tx.user_id,
        invoice_id=tx.invoice_id,
        type=tx.type.value if hasattr(tx.type, "value") else str(tx.type),
        amount=tx.amount,
        balance_after=tx.balance_after,
        purpose=tx.purpose,
        order_number=tx.order_number,
        description=tx.description,
        created_at=tx.created_at,
    )


@router.get("/favorites", response_model=FavoritesResponse)
async def profile_favorites(
    user_id: int = Query(...),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(service_session),
) -> FavoritesResponse:
    await _get_client_or_404(session, user_id)
    repo = FavoriteRepository(session)
    favorites, total = await repo.get_by_user_paginated(user_id, query=q, page=page, per_page=per_page)

    items = []
    for fav in favorites:
        form = fav.form
        if not form:
            continue
        profile = form.profile
        pricing = form.pricing
        publication = form.publication
        photos = [p.storage_key for p in getattr(form, "photos", []) if p.storage_key]
        first_photo = photos[0] if photos else None

        items.append(
            FavoriteItem(
                form_id=form.id,
                form_code=form.code,
                name=profile.name if profile else form.code,
                age=int(profile.age or 0) if profile else 0,
                height=int(profile.height or 0) if profile else 0,
                bust_size=int(profile.bust_size or 0) if profile else 0,
                price_1h=pricing.one_hour_price if pricing else None,
                city_slot=publication.city_slot if publication else 1,
                photo_url=first_photo,
                photos=photos,
            )
        )
    return FavoritesResponse(items=items, total=total, page=page, per_page=per_page)


@router.post("/promo", response_model=PromoActivateResponse)
async def activate_promo(
    payload: PromoActivateRequest,
    user_id: int = Query(...),
    session: AsyncSession = Depends(service_session),
) -> PromoActivateResponse:
    service = ClientService(session)
    client = await service.get_client(user_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    clean_code = (payload.code or "").strip()
    promo = await service.promos.get_by_code(clean_code)
    if not promo:
        return PromoActivateResponse(applied=False, promo_code=None)
    await service.set_promo(user_id, promo.code)
    await emit_client_log(
        "promocode_activated",
        client,
        code=promo.code,
        amount=str(getattr(promo, "discount_amount", 0)),
    )
    return PromoActivateResponse(applied=True, promo_code=promo.code)

