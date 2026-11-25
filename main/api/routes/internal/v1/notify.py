from __future__ import annotations

import logging
from aiogram import Bot
from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from shared.bot.utils.media_banner import bot_send_banner

router = APIRouter(prefix="/internal/v1/notify", tags=["internal-notify"])
logger = logging.getLogger(__name__)


class InvoiceStatusNotifyRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    user_id: int
    order_id: int | str
    status: str  # "confirmed", "paid", "rejected"
    purpose: str = "order"
    amount: int = 0
    form_code: str | None = None
    model_name: str | None = None
    tariff: str | None = None


@router.post("/invoice-status")
async def notify_invoice_status(payload: InvoiceStatusNotifyRequest, request: Request):
    bot: Bot = getattr(request.app.state, "bot", None)
    if not bot:
        logger.error("Bot instance not found on app.state")
        return {"ok": False, "error": "bot_not_found"}

    order_str = str(payload.order_id)
    model_str = payload.model_name or payload.form_code or "—"
    tariff_str = payload.tariff or "Стандарт"
    price_str = f"{payload.amount:,}".replace(",", " ")
    is_deposit = payload.purpose in ("deposit", "top_up")

    if payload.status in ("confirmed", "paid"):
        if is_deposit:
            text = t(
                "top_up_confirmed",
                order_number=order_str,
                price=price_str,
            )
            banner = get_banner_file("payment-success-banner")
        else:
            text = t(
                "models_check_confirmed",
                order_number=order_str,
                model_name=model_str,
                tariff=tariff_str,
                price=price_str,
            )
            banner = get_banner_file("payment-success-banner")
        try:
            await bot_send_banner(
                bot,
                payload.user_id,
                text,
                banner=banner,
            )
        except Exception as exc:
            logger.warning("Failed to send payment confirmed notification to user %s: %s", payload.user_id, exc)
    elif payload.status == "rejected":
        if is_deposit:
            text = t(
                "top_up_rejected",
                order_number=order_str,
                price=price_str,
            )
            banner = get_banner_file("payment-unavailable-banner")
        else:
            text = t(
                "models_check_rejected",
                order_number=order_str,
            )
            banner = get_banner_file("payment-unavailable-banner")
        try:
            await bot_send_banner(
                bot,
                payload.user_id,
                text,
                banner=banner,
            )
        except Exception as exc:
            logger.warning("Failed to send payment rejected notification to user %s: %s", payload.user_id, exc)

    return {"ok": True}


class DirectMessageRequest(BaseModel):
    user_id: int
    text: str


@router.post("/direct-message")
async def send_direct_message(payload: DirectMessageRequest, request: Request):
    bot: Bot = getattr(request.app.state, "bot", None)
    if not bot:
        logger.error("Bot instance not found on app.state")
        return {"ok": False, "error": "bot_not_found"}
    try:
        await bot.send_message(payload.user_id, payload.text, parse_mode="HTML")
        return {"ok": True}
    except Exception as exc:
        logger.warning("Failed to send direct message to user %s: %s", payload.user_id, exc)
        return {"ok": False, "error": str(exc)}
