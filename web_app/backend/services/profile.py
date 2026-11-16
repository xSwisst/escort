from __future__ import annotations

from backend.schemas.profile import (
    ProfileAddressItem,
    ProfileAddressResponse,
    ProfileCityResponse,
    ProfileClientResponse,
    ProfileOrderHistoryItem,
    ProfileOrdersPagination,
    ProfileOrdersResponse,
    ProfilePromo,
    ProfilePromoResponse,
    ProfileResponse,
    ProfileUserResponse,
)


def build_profile_client(profile, *, agreement_accepted: bool) -> ProfileClientResponse:
    date_register_str = None
    if getattr(profile, "registered_at", None):
        reg = profile.registered_at
        date_register_str = reg.isoformat() if hasattr(reg, "isoformat") else str(reg)

    first_city = getattr(profile, "primary_city", None)
    second_city = getattr(profile, "secondary_city", None)
    active_slot = int(getattr(profile, "active_city_slot", 1) or 1)

    return ProfileClientResponse(
        worker_id=getattr(profile, "worker_id", None),
        agreement_accepted=agreement_accepted,
        agreement_id=str(getattr(profile, "agreement_id", "") or "") or None,
        is_banned=bool(getattr(profile, "is_banned", False)),
        city_status=active_slot,
        first_city=first_city,
        second_city=second_city,
        orders=int(getattr(profile, "orders", 0) or 0),
        rating=float(getattr(profile, "rating", 0.0) or 0.0),
        promo=getattr(profile, "promo", None),
        promo_amount=getattr(profile, "promo_amount", None),
        date_register=date_register_str,
        address_system_enabled=True,
        balance=int(getattr(profile, "balance", 0) or 0),
    )


def build_profile_response(*, session_payload: dict, profile, addresses) -> ProfileResponse:
    return ProfileResponse(
        user=ProfileUserResponse(
            telegram_id=int(session_payload["telegram_id"]),
            first_name=session_payload.get("first_name"),
            last_name=session_payload.get("last_name"),
            username=session_payload.get("username"),
            photo_url=session_payload.get("photo_url"),
            is_mock=bool(session_payload.get("is_mock", False)),
        ),
        client=build_profile_client(profile, agreement_accepted=bool(session_payload.get("agreement_accepted", False))),
        addresses=[
            ProfileAddressItem(
                id=item.id,
                title=item.title,
                address=item.address,
                created_at=item.created_at.isoformat() if getattr(item, "created_at", None) and hasattr(item.created_at, "isoformat") else str(getattr(item, "created_at", "") or "") or None,
            )
            for item in getattr(addresses, "items", [])
        ],
    )


def build_profile_city_response(*, profile, agreement_accepted: bool) -> ProfileCityResponse:
    return ProfileCityResponse(client=build_profile_client(profile, agreement_accepted=agreement_accepted))


def build_profile_address_response(addresses) -> ProfileAddressResponse:
    return ProfileAddressResponse(
        addresses=[
            ProfileAddressItem(
                id=item.id,
                title=item.title,
                address=item.address,
                created_at=item.created_at.isoformat() if getattr(item, "created_at", None) and hasattr(item.created_at, "isoformat") else str(getattr(item, "created_at", "") or "") or None,
            )
            for item in getattr(addresses, "items", [])
        ]
    )


def build_profile_promo_response(*, result, active_promo: str | None, profile=None, agreement_accepted: bool = True) -> ProfilePromoResponse:
    applied = bool(getattr(result, "applied", False))
    promo_code = getattr(result, "promo_code", active_promo)
    discount_amount = getattr(result, "discount_amount", None)
    return ProfilePromoResponse(
        promo=ProfilePromo(
            code=promo_code,
            amount=discount_amount,
            is_active=bool(applied or active_promo),
        ),
        client=build_profile_client(profile, agreement_accepted=agreement_accepted) if profile else None,
    )


def build_profile_orders_response(orders, page: int = 1, page_size: int = 100) -> ProfileOrdersResponse:
    items = [
        ProfileOrderHistoryItem(
            number=item.order_number,
            date=item.created_at.isoformat() if getattr(item, "created_at", None) and hasattr(item.created_at, "isoformat") else str(getattr(item, "created_at", "") or "") or None,
            model_info=getattr(item, "form_snapshot", None),
            city=getattr(item, "city", None),
            status=getattr(item, "status", "pending"),
            tariff_plan=getattr(item, "tariff_plan", None),
            promo=getattr(item, "promo_code", None),
        )
        for item in getattr(orders, "items", [])
    ]
    total = len(items)
    return ProfileOrdersResponse(
        items=items,
        pagination=ProfileOrdersPagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=max(1, (total + page_size - 1) // page_size),
        ),
    )
