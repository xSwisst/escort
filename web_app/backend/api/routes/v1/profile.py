from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.dependencies import user_session_auth
from backend.clients.api import api_client
from backend.schemas import (
    ProfileAddressCreateRequest,
    ProfileAddressResponse,
    ProfileCityResponse,
    ProfileCityStatusUpdateRequest,
    ProfileCityUpdateRequest,
    ProfileOrdersResponse,
    ProfilePromoActivateRequest,
    ProfilePromoResponse,
    ProfileResponse,
)
from backend.services import (
    build_profile_address_response,
    build_profile_city_response,
    build_profile_orders_response,
    build_profile_promo_response,
    build_profile_response,
)

router = APIRouter(prefix="/web-app/api/v1/profile", tags=["web-app-profile"])


async def _profile_payload(user_id: int):
    profile = await api_client.client_v1.get_profile(user_id=user_id)
    addresses = await api_client.client_v1.list_addresses(user_id=user_id)
    return profile, addresses


@router.get("", response_model=ProfileResponse)
async def get_profile(session_payload: dict = Depends(user_session_auth)) -> ProfileResponse:
    user_id = int(session_payload["user_id"])
    profile, addresses = await _profile_payload(user_id)
    return build_profile_response(session_payload=session_payload, profile=profile, addresses=addresses)


@router.put("/city", response_model=ProfileCityResponse)
async def set_city(payload: ProfileCityUpdateRequest, session_payload: dict = Depends(user_session_auth)) -> ProfileCityResponse:
    user_id = int(session_payload["user_id"])
    await api_client.client_v1.set_city(user_id=user_id, city=payload.cityName, slot=payload.slot)
    profile = await api_client.client_v1.get_profile(user_id=user_id)
    return build_profile_city_response(profile=profile, agreement_accepted=bool(session_payload.get("agreement_accepted", False)))


@router.put("/city-status", response_model=ProfileCityResponse)
async def set_active_city_slot(payload: ProfileCityStatusUpdateRequest, session_payload: dict = Depends(user_session_auth)) -> ProfileCityResponse:
    user_id = int(session_payload["user_id"])
    await api_client.client_v1.switch_city(user_id=user_id, active_city_slot=payload.cityStatus)
    profile = await api_client.client_v1.get_profile(user_id=user_id)
    return build_profile_city_response(profile=profile, agreement_accepted=bool(session_payload.get("agreement_accepted", False)))


@router.put("/address", response_model=ProfileAddressResponse)
async def create_address(payload: ProfileAddressCreateRequest, session_payload: dict = Depends(user_session_auth)) -> ProfileAddressResponse:
    user_id = int(session_payload["user_id"])
    await api_client.client_v1.create_address(
        user_id=user_id,
        title=payload.title,
        address=payload.address,
    )
    addresses = await api_client.client_v1.list_addresses(user_id=user_id)
    return build_profile_address_response(addresses)


@router.delete("/address/{address_id}", response_model=ProfileAddressResponse)
async def delete_address(address_id: int, session_payload: dict = Depends(user_session_auth)) -> ProfileAddressResponse:
    user_id = int(session_payload["user_id"])
    await api_client.client_v1.delete_address(user_id=user_id, address_id=address_id)
    addresses = await api_client.client_v1.list_addresses(user_id=user_id)
    return build_profile_address_response(addresses)


@router.get("/promo", response_model=ProfilePromoResponse)
async def get_promo(session_payload: dict = Depends(user_session_auth)) -> ProfilePromoResponse:
    profile = await api_client.client_v1.get_profile(user_id=int(session_payload["user_id"]))
    return build_profile_promo_response(
        result=None,
        active_promo=profile.promo,
        profile=profile,
        agreement_accepted=bool(session_payload.get("agreement_accepted", False)),
    )


@router.put("/promo", response_model=ProfilePromoResponse)
async def activate_promo(payload: ProfilePromoActivateRequest, session_payload: dict = Depends(user_session_auth)) -> ProfilePromoResponse:
    user_id = int(session_payload["user_id"])
    result = await api_client.client_v1.activate_promo(user_id=user_id, code=payload.code)
    profile = await api_client.client_v1.get_profile(user_id=user_id)
    return build_profile_promo_response(
        result=result,
        active_promo=profile.promo,
        profile=profile,
        agreement_accepted=bool(session_payload.get("agreement_accepted", False)),
    )


@router.get("/orders", response_model=ProfileOrdersResponse)
async def get_orders(session_payload: dict = Depends(user_session_auth)) -> ProfileOrdersResponse:
    orders = await api_client.client_v1.get_orders(user_id=int(session_payload["user_id"]))
    return build_profile_orders_response(orders)
