from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.assets.texts import t

router = Router(name="support_start")


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(msg: Message) -> None:
    await msg.answer(t("welcome"), parse_mode="HTML")


@router.message(Command("info"), F.chat.type == "private")
async def cmd_info(msg: Message) -> None:
    await msg.answer(t("info"), parse_mode="HTML")
