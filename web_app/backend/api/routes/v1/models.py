from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import user_session_auth
from backend.clients.api import api_client
from backend.schemas.bookings import (
    BookingAdditionalItem,
    BookingPaymentMethodItem,
    BookingPrepareRequest,
    BookingPrepareResponse,
    BookingTariffInfo,
)
from backend.schemas.models import FavoriteCodesResponse, ModelDetailsResponse, ModelListResponse
from backend.services.models import build_favorite_codes_response, build_model_details_response, build_model_list_response

router = APIRouter(prefix="/web-app/api/v1/models", tags=["web-app-models"])


@router.get("", response_model=ModelListResponse)
async def list_models(session_payload: dict = Depends(user_session_auth)) -> ModelListResponse:
    forms = await api_client.client_v1.list_forms(user_id=int(session_payload["user_id"]))
    return build_model_list_response(forms)


@router.get("/favorites/codes", response_model=FavoriteCodesResponse)
async def get_favorite_codes(session_payload: dict = Depends(user_session_auth)) -> FavoriteCodesResponse:
    favorites = await api_client.client_v1.get_favorites(user_id=int(session_payload["user_id"]))
    return build_favorite_codes_response(favorites)


@router.put("/{form_code}/favorite", response_model=FavoriteCodesResponse)
async def add_favorite(form_code: str, session_payload: dict = Depends(user_session_auth)) -> FavoriteCodesResponse:
    user_id = int(session_payload["user_id"])
    favorites = await api_client.client_v1.get_favorites(user_id=user_id)
    codes = {item["form_code"] if isinstance(item, dict) else item.form_code for item in getattr(favorites, "items", [])}
    if form_code not in codes:
        await api_client.client_v1.toggle_favorite(user_id=user_id, form_code=form_code)
    updated = await api_client.client_v1.get_favorites(user_id=user_id)
    return build_favorite_codes_response(updated)


@router.delete("/{form_code}/favorite", response_model=FavoriteCodesResponse)
async def remove_favorite(form_code: str, session_payload: dict = Depends(user_session_auth)) -> FavoriteCodesResponse:
    user_id = int(session_payload["user_id"])
    favorites = await api_client.client_v1.get_favorites(user_id=user_id)
    codes = {item["form_code"] if isinstance(item, dict) else item.form_code for item in getattr(favorites, "items", [])}
    if form_code in codes:
        await api_client.client_v1.toggle_favorite(user_id=user_id, form_code=form_code)
    updated = await api_client.client_v1.get_favorites(user_id=user_id)
    return build_favorite_codes_response(updated)


@router.post("/{form_code}/opened")
async def mark_model_opened(form_code: str, session_payload: dict = Depends(user_session_auth)) -> dict:
    user_id = int(session_payload["user_id"])
    try:
        await api_client.client_v1.get_form_card(user_id=user_id, form_code=form_code)
    except Exception:
        pass
    return {"ok": True}


@router.post("/{form_code}/booking/prepare", response_model=BookingPrepareResponse)
async def prepare_booking(
    form_code: str,
    payload: BookingPrepareRequest,
    session_payload: dict = Depends(user_session_auth),
) -> BookingPrepareResponse:
    user_id = int(session_payload["user_id"])
    card = await api_client.client_v1.get_form_card(user_id=user_id, form_code=form_code)
    additionals_data = await api_client.client_v1.get_additionals(form_code=form_code)

    tariff_prices = {
        "1h": int(getattr(card, "one_hour_price", 0) or 0),
        "2h": int(getattr(card, "two_hour_price", 0) or 0),
        "3h": int(getattr(card, "three_hour_price", 0) or 0),
        "night": int(getattr(card, "overnight_price", 0) or 0),
    }
    tariff_amount = tariff_prices.get(payload.tariff, tariff_prices["1h"])

    selected_additionals = []
    additional_sum = 0
    all_additionals = getattr(additionals_data, "items", [])
    for idx, a in enumerate(all_additionals):
        add_id = idx + 1
        if add_id in payload.additionals:
            name = a.get("name", "") if isinstance(a, dict) else getattr(a, "name", str(a))
            price = int(a.get("price", 0) if isinstance(a, dict) else getattr(a, "price", 0))
            selected_additionals.append(BookingAdditionalItem(id=add_id, name=str(name), price=price))
            additional_sum += price

    total_amount = max(0, tariff_amount + additional_sum - int(getattr(card, "discount_amount", 0) or 0))
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    return BookingPrepareResponse(
        order_number=order_number,
        model_name=card.name,
        model_code=form_code,
        amount=total_amount,
        additional_sum=additional_sum,
        currency="RUB",
        tariff=BookingTariffInfo(key=payload.tariff, amount=tariff_amount),
        additionals=selected_additionals,
        payment_methods=[
            BookingPaymentMethodItem(key="card"),
            BookingPaymentMethodItem(key="cash"),
        ],
    )


@router.get("/{form_code}", response_model=ModelDetailsResponse)
async def get_model(form_code: str, session_payload: dict = Depends(user_session_auth)) -> ModelDetailsResponse:
    user_id = int(session_payload["user_id"])
    card = await api_client.client_v1.get_form_card(user_id=user_id, form_code=form_code)
    reviews = await api_client.client_v1.get_reviews(form_code=form_code)
    services = await api_client.client_v1.get_services(form_code=form_code)
    additionals = await api_client.client_v1.get_additionals(form_code=form_code)
    return build_model_details_response(card, reviews=reviews, services=services, additionals=additionals)
