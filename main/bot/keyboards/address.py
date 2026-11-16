from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn, nav_buttons
from core.settings import settings

MODELS_PER_PAGE = 9

def kb_address_list(addresses: list, page: int = 0):
    per_page = MODELS_PER_PAGE
    total_pages = max(1, (len(addresses) + per_page - 1) // per_page)
    start = page * per_page
    page_items = addresses[start:start + per_page]

    builder = InlineKeyboardBuilder()
    for address in page_items:
        builder.row(InlineKeyboardButton(text=address.title, callback_data=f"addr:view:{address.id}"))
    navigation = nav_buttons(page + 1, total_pages, "addr_page")
    if navigation:
        builder.row(*navigation)
    builder.row(InlineKeyboardButton(**btn("add_address", callback_data="addr:add")))
    builder.row(back_btn("back_to_profile", "menu:profile"))
    return builder.as_markup()


def kb_address_detail(address_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("edit_address", callback_data=f"addr:edit:{address_id}")))
    builder.row(InlineKeyboardButton(**btn("delete_address", callback_data=f"addr:del:{address_id}")))
    builder.row(back_btn("back_to_addresses", "addr:list"))
    return builder.as_markup()


def kb_address_delete_confirm(address_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data=f"addr:del_yes:{address_id}")))
    builder.row(back_btn("back_to_address", f"addr:view:{address_id}"))
    return builder.as_markup()


def kb_address_edit(address_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("edit_title", callback_data=f"addr:edit_title:{address_id}")))
    builder.row(InlineKeyboardButton(**btn("edit_addr", callback_data=f"addr:edit_addr:{address_id}")))
    builder.row(back_btn("back_to_address", f"addr:view:{address_id}"))
    return builder.as_markup()


def kb_address_create_confirm():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data="addr:add_yes")))
    builder.row(back_btn("back_to_addresses", "addr:add_cancel"))
    return builder.as_markup()


def kb_address_edit_title_confirm(address_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data=f"addr:edit_title_yes:{address_id}")))
    builder.row(back_btn("back_to_address", f"addr:view:{address_id}"))
    return builder.as_markup()


def kb_address_edit_addr_confirm(address_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data=f"addr:edit_addr_yes:{address_id}")))
    builder.row(back_btn("back_to_address", f"addr:view:{address_id}"))
    return builder.as_markup()

