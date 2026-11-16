from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.keyboards.info import (
    kb_additionals_menu,
    kb_back_additionals,
    kb_back_info,
    kb_faq,
    kb_info,
)
from clients.api import api_client
from shared.bot.utils.media_banner import edit_banner

router = Router(name="info")



async def _edit_info(call: CallbackQuery, text: str, reply_markup):
    await edit_banner(call.message, text, banner=get_banner_file("info-banner"), reply_markup=reply_markup)


async def _get_document_url(user_id: int) -> str | None:
    agreement = await api_client.info.get_agreement(user_id)
    return agreement.document_url


@router.callback_query(F.data == "menu:info")
async def show_info(call: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    text = t("info_main", bot_name=bot_info.full_name)
    document_url = await _get_document_url(call.from_user.id)
    await _edit_info(call, text, kb_info(document_url=document_url))


@router.callback_query(F.data == "info:faq")
async def show_faq(call: CallbackQuery):
    await _edit_info(call, t("info_faq_1"), kb_faq(selected=1))


@router.callback_query(F.data.regexp(r"^question:\d+$"))
async def question_page(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    text = t(f"info_faq_{page}") if page in (1, 2, 3) else t("info_faq_1")
    await _edit_info(call, text, kb_faq(selected=page))


@router.callback_query(F.data == "info:guarantees")
async def show_guarantees(call: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    await _edit_info(call, t("info_guarantees", bot_name=bot_info.full_name), kb_back_info())


@router.callback_query(F.data == "info:additionals")
async def show_additionals(call: CallbackQuery):
    await _edit_info(call, t("info_additionals"), kb_additionals_menu())


@router.callback_query(F.data == "info:add_info")
async def show_additionals_info(call: CallbackQuery):
    await _edit_info(call, t("info_additionals_info"), kb_back_additionals())


_ADDITIONALS_TEXTS = {
    "shootings": t("info_additionals_shootings"),
    "accompaniment": t("info_additionals_accompaniment"),
    "relations": t("info_additionals_relations"),
    "promo_s": t("info_additionals_promo"),
    "hostess": t("info_additionals_hostess"),
}


@router.callback_query(F.data.startswith("info:sub:"))
async def show_additionals_sub(call: CallbackQuery):
    key = call.data.split(":")[2]
    await _edit_info(call, _ADDITIONALS_TEXTS.get(key, t("info_section_unavailable")), kb_back_additionals())



@router.callback_query(F.data == "back-info:info")
async def back_info(call: CallbackQuery, bot: Bot):
    await show_info(call, bot)
