from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn


def kb_user_info(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("change_agreement", callback_data=f"support:change-agreement:{user_id}")))
    builder.row(InlineKeyboardButton(**btn("refresh", callback_data=f"support:refresh-user:{user_id}")))
    return builder.as_markup()


def kb_agreements(agreements: list, user_id: int):
    builder = InlineKeyboardBuilder()
    for agreement in agreements:
        builder.row(
            InlineKeyboardButton(
                text=agreement.title,
                callback_data=f"support:set-agreement:{user_id}:{agreement.agreement_id}",
            )
        )
    builder.row(InlineKeyboardButton(**btn("back", callback_data=f"support:back-user:{user_id}")))
    return builder.as_markup()
