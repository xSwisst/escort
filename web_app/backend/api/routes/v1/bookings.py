from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.dependencies import user_session_auth
from backend.schemas.bookings import BookingPaymentRequest, BookingPaymentResponse

router = APIRouter(prefix="/web-app/api/v1/bookings", tags=["web-app-bookings"])


@router.post("/{order_number}/payment", response_model=BookingPaymentResponse)
async def resolve_booking_payment(
    order_number: str,
    payload: BookingPaymentRequest,
    session_payload: dict = Depends(user_session_auth),
) -> BookingPaymentResponse:
    if payload.payment_method == "cash":
        return BookingPaymentResponse(
            order_number=order_number,
            model_name="Model",
            model_code="model",
            amount=0,
            currency="RUB",
            payment_method="cash",
            status="cash_unavailable",
        )

    return BookingPaymentResponse(
        order_number=order_number,
        model_name="Model",
        model_code="model",
        amount=0,
        currency="RUB",
        payment_method=payload.payment_method,
        status="manual_support",
    )
