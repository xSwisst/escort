from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .invoices import router as invoices_router

router = Router(name="logs_base")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Logs service bot is active.")


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer("Logs service is running.")


def get_routers() -> list[Router]:
    return [router, invoices_router]


__all__ = ["get_routers"]
