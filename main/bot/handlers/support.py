from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.keyboards.support import kb_support_menu
from clients.logs import emit_log_event
from shared.bot.utils.media_banner import edit_banner

router = Router(name="support")


@router.callback_query(F.data == "menu:support")
async def show_support(call: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    await edit_banner(
        call.message,
        t("support_caption", name=bot_info.full_name),
        banner=get_banner_file("support-banner"),
        reply_markup=kb_support_menu(),
    )
    await call.answer()
    await emit_log_event(
        "open_support_section",
        call.from_user.id,
        {
            "user_id": call.from_user.id,
            "first_name": call.from_user.first_name or "",
            "last_name": call.from_user.last_name or "",
            "username": call.from_user.username,
        },
    )
