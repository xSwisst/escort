from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.handlers.models_shared import get_form_card_payload
from bot.keyboards.common import kb_back
from bot.states import SearchCodeState
from shared.bot.utils.media_banner import bot_edit_banner, bot_edit_photo, edit_banner
from utils.helpers import models_banner_media

router = Router(name="search_with_code")


@router.callback_query(F.data == "menu:search_code")
async def start_search(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SearchCodeState.code)
    await state.update_data(bot_msg_id=call.message.message_id)
    await edit_banner(
        call.message,
        t("search_code_enter"),
        banner=get_banner_file("enter-model-code-banner"),
        reply_markup=kb_back("back_to_main", "menu:main"),
    )
    await call.answer()


@router.message(SearchCodeState.code)
async def process_search(msg: Message, state: FSMContext, bot: Bot):
    del bot
    await msg.delete()
    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id") or (msg.message_id - 1)
    code = (msg.text or "").strip().upper()
    if not code:
        return

    card = await get_form_card_payload(
        msg.from_user.id,
        code,
        fallback_media=models_banner_media(),
    )

    if not card:
        await bot_edit_banner(
            msg.bot,
            msg.chat.id,
            bot_msg_id,
            t("search_code_not_found", code=code),
            banner=get_banner_file("code-not-found-banner"),
            reply_markup=kb_back("back_to_main", "menu:main"),
        )
        return

    await state.clear()
    first_media, text, markup = card

    await bot_edit_photo(
        msg.bot,
        msg.chat.id,
        bot_msg_id,
        text,
        first_media,
        reply_markup=markup,
    )
