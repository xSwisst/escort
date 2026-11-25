from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn


def _city_button(city_name: str, active: bool, callback_data: str):
    btn_key = "current_city" if active else "other_city"
    return InlineKeyboardButton(**btn(btn_key, city=city_name, callback_data=callback_data))



def kb_profile(primary_city: str | None = None, *, show_addresses: bool = True):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(**btn("top_up", callback_data="profile:top_up")),
    )
    builder.row(
        InlineKeyboardButton(**btn("transactions_history", switch_inline_query_current_chat="my_transactions?search=")),
        InlineKeyboardButton(**btn("orders", switch_inline_query_current_chat="my_orders?search=")),
    )

    builder.row(
        InlineKeyboardButton(**btn("my_addresses", callback_data="addr:list")),
        InlineKeyboardButton(**btn("favorites", switch_inline_query_current_chat="my_favorites?search=")),
    )
    builder.row(
        InlineKeyboardButton(**btn("promo", callback_data="profile:promo")),
        InlineKeyboardButton(**btn("change_city", callback_data="profile:city")),
    )
    builder.row(back_btn("back_to_main", "menu:main"))
    return builder.as_markup()


def kb_top_up_methods():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(**btn("pay_card", callback_data="top_up:method:card")),
    )
    builder.row(back_btn("back_to_profile", "menu:profile"))
    return builder.as_markup()


def kb_profile_detail_back():
    builder = InlineKeyboardBuilder()
    builder.row(back_btn("back_to_profile", "menu:profile"))
    return builder.as_markup()


def kb_city_management(
    primary_city: str | None = None,
    secondary_city: str | None = None,
    active_city_slot: int = 1,
    *,
    cities: list | None = None,
):
    builder = InlineKeyboardBuilder()
    if cities:
        for city_item in cities:
            slot = getattr(city_item, "slot", 1)
            name = getattr(city_item, "city_name", None)
            if name:
                builder.row(_city_button(name, active_city_slot == slot, f"city:switch:{slot}"))
    else:
        if primary_city:
            builder.row(_city_button(primary_city, active_city_slot == 1, "city:switch:1"))
        if secondary_city:
            builder.row(_city_button(secondary_city, active_city_slot == 2, "city:switch:2"))
    builder.row(InlineKeyboardButton(**btn("add_city", callback_data="city:add")))
    builder.row(back_btn("back_to_profile", "menu:profile"))
    return builder.as_markup()


def kb_orders_type():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("active_orders", callback_data="orders:active")))
    builder.row(InlineKeyboardButton(**btn("completed_orders", callback_data="orders:completed")))
    builder.row(back_btn("back_to_profile", "menu:profile"))
    return builder.as_markup()


