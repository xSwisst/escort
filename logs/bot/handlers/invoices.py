from __future__ import annotations

import logging
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import httpx

from core.settings import settings
from shared.auth import create_service_token

logger = logging.getLogger(__name__)

router = Router(name="logs_invoices")


def _get_auth_headers() -> dict[str, str]:
    if not settings.API_SECRET_KEY:
        return {}
    token = create_service_token(
        secret_key=settings.API_SECRET_KEY,
        issuer=settings.API_AUDIENCE,
        audience=settings.API_TARGET_AUDIENCE,
        ttl_hours=1,
    )
    return {"Authorization": f"Bearer {token}"}


@router.callback_query(F.data.startswith("log:inv:"))
async def handle_invoice_action(call: CallbackQuery) -> None:
    parts = (call.data or "").split(":")
    if len(parts) != 4:
        await call.answer()
        return

    _, _, action, invoice_number = parts

    actor_name = f"@{call.from_user.username}" if call.from_user.username else (call.from_user.first_name or "Админ")

    if action not in ("appr", "rej"):
        await call.answer()
        return

    endpoint = "approve" if action == "appr" else "reject"
    url = f"{settings.API_BASE_URL.rstrip('/')}/internal/v1/invoices/{invoice_number}/{endpoint}"

    payload = {
        "admin_username": call.from_user.username,
        "confirmed_by_admin_id": call.from_user.id,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=_get_auth_headers())
            if resp.status_code == 200:
                status_text = f"✅ Подтверждено ({actor_name})" if action == "appr" else f"❌ Отклонено ({actor_name})"
                new_markup = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=status_text,
                                callback_data="noop",
                            )
                        ]
                    ]
                )
                try:
                    if call.message:
                        await call.message.edit_reply_markup(reply_markup=new_markup)
                except Exception as exc:
                    logger.warning("Failed to edit reply markup: %s", exc)

                await call.answer(
                    "Чек подтвержден!" if action == "appr" else "Чек отклонен!",
                    show_alert=True,
                )
                return
            elif resp.status_code == 400:
                await call.answer("Чек уже был обработан.", show_alert=True)
                return
            else:
                logger.error("API error %d when processing invoice: %s", resp.status_code, resp.text)
                await call.answer("Ошибка при обработке чека.", show_alert=True)
                return
    except Exception as exc:
        logger.exception("Failed to contact API for invoice action: %s", exc)
        await call.answer("Ошибка соединения с сервером.", show_alert=True)


@router.callback_query(F.data == "noop")
async def handle_noop(call: CallbackQuery) -> None:
    await call.answer()
