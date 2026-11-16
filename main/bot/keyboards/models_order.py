from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn, nav_buttons
from core.settings import settings

MODELS_PER_PAGE = 9

def tariff_label(code: str) -> str:
    key_map = {
        "1h": "tariff_hour",
        "2h": "tariff_2hours",
        "3h": "tariff_3hours",
        "night": "tariff_night",
        "private": "tariff_private",
    }
    key = key_map.get(code)
    return btn(key)["text"] if key else code


def kb_tariff(
    form_code: str,
    *,
    has_one_hour: bool = True,
    has_two_hours: bool = False,
    has_three_hours: bool = True,
    has_night: bool = True,
):
    builder = InlineKeyboardBuilder()
    buttons = []
    if has_one_hour:
        buttons.append(InlineKeyboardButton(**btn("tariff_hour", callback_data=f"tariff:{form_code}:1h")))
    if has_two_hours:
        buttons.append(InlineKeyboardButton(**btn("tariff_2hours", callback_data=f"tariff:{form_code}:2h")))
    if has_three_hours:
        buttons.append(InlineKeyboardButton(**btn("tariff_3hours", callback_data=f"tariff:{form_code}:3h")))
    if has_night:
        buttons.append(InlineKeyboardButton(**btn("tariff_night", callback_data=f"tariff:{form_code}:night")))
    for index in range(0, len(buttons), 2):
        builder.row(*buttons[index:index + 2])
    builder.row(back_btn("back_to_place", "order:back_to_place"))
    return builder.as_markup()


def kb_months(form_code: str, months: list[tuple[int, int]]):
    builder = InlineKeyboardBuilder()
    for year, month in months:
        builder.row(InlineKeyboardButton(text=f"{btn(f'month_{month}')['text']} {year}", callback_data=f"order:month:{form_code}:{year}:{month}"))
    builder.row(back_btn("back_to_model", f"model:view:{form_code}"))
    return builder.as_markup()


def kb_dates(form_code: str, dates: list[int], year: int, month: int):
    builder = InlineKeyboardBuilder()
    row_buttons = []
    for day in dates:
        row_buttons.append(InlineKeyboardButton(text=f"{day:02d}.{month:02d}", callback_data=f"order:date:{form_code}:{year}:{month}:{day}"))
        if len(row_buttons) == 3:
            builder.row(*row_buttons)
            row_buttons = []
    if row_buttons:
        builder.row(*row_buttons)
    builder.row(back_btn("back_to_months", f"model:order:{form_code}"))
    return builder.as_markup()


def kb_times(form_code: str, times: list[str], date_key: str):
    builder = InlineKeyboardBuilder()
    row_buttons = []
    for item in times:
        row_buttons.append(InlineKeyboardButton(text=item, callback_data=f"order:time:{form_code}:{date_key}:{item}"))
        if len(row_buttons) == 3:
            builder.row(*row_buttons)
            row_buttons = []
    if row_buttons:
        builder.row(*row_buttons)
    year, month, _ = date_key.split(":")
    builder.row(back_btn("back_to_dates", f"order:month:{form_code}:{year}:{month}"))
    return builder.as_markup()


def kb_meeting_place_type(form_code: str, date_key: str | None = None, time_value: str | None = None):
    builder = InlineKeyboardBuilder()
    normalized_date_key = str(date_key or "").strip()
    normalized_time_value = str(time_value or "").strip()
    if normalized_date_key and normalized_time_value:
        model_callback = f"order:place:{form_code}:{normalized_date_key}:{normalized_time_value}:model"
        client_callback = f"order:place:{form_code}:{normalized_date_key}:{normalized_time_value}:client"
        back_callback = f"order:date:{form_code}:{normalized_date_key}"
        back_text_key = "back_to_times"
    else:
        model_callback = f"order:place-direct:{form_code}:model"
        client_callback = f"order:place-direct:{form_code}:client"
        back_callback = f"model:view:{form_code}"
        back_text_key = "back_to_model"
    builder.row(InlineKeyboardButton(**btn("place_at_model", callback_data=model_callback)))
    builder.row(InlineKeyboardButton(**btn("place_at_mine", callback_data=client_callback)))
    builder.row(back_btn(back_text_key, back_callback))
    return builder.as_markup()


def kb_order_address_select(addresses: list, page: int = 0):
    per_page = MODELS_PER_PAGE
    total_pages = max(1, (len(addresses) + per_page - 1) // per_page)
    start = page * per_page
    page_items = addresses[start:start + per_page]

    builder = InlineKeyboardBuilder()
    for address in page_items:
        builder.row(InlineKeyboardButton(text=address.title, callback_data=f"oaddr:sel:{address.id}"))
    navigation = nav_buttons(page + 1, total_pages, "oaddr_page")
    if navigation:
        builder.row(*navigation)
    builder.row(InlineKeyboardButton(**btn("add_address", callback_data="oaddr:add")))
    builder.row(back_btn("back_to_place", "oaddr:back"))
    return builder.as_markup()


def kb_order_address_create_confirm():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data="oaddr:add_yes")))
    builder.row(back_btn("back_to_addresses", "oaddr:add_cancel"))
    return builder.as_markup()


def kb_meeting_place(form_code: str, date_key: str | None = None, time_value: str | None = None):
    return kb_meeting_place_type(form_code, date_key, time_value)


def kb_addons(
    addons: list[tuple[str, int]],
    selected: set[int],
    order_number: str,
    form_code: str,
):
    builder = InlineKeyboardBuilder()
    for i, (name, price) in enumerate(addons):
        icon = "🟢" if i in selected else "⚪️"
        text = f"{icon} {name}" + (f" — {price}₽" if price else "")
        builder.row(InlineKeyboardButton(text=text, callback_data=f"addon:toggle:{order_number}:{i}"))
    builder.row(InlineKeyboardButton(**btn("next", callback_data=f"addon:next:{order_number}")))
    builder.row(InlineKeyboardButton(**btn("back", callback_data=f"addon:back:{order_number}")))
    return builder.as_markup()


def kb_payment_method(order_number: str):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(**btn("pay_card", callback_data=f"pay:method:{order_number}:card")),
        InlineKeyboardButton(**btn("pay_cash", callback_data=f"pay:method:{order_number}:cash")),
    )
    builder.row(
        InlineKeyboardButton(**btn("pay_balance", callback_data=f"pay:method:{order_number}:balance")),
    )
    builder.row(InlineKeyboardButton(**btn("back", callback_data=f"pay_back_addons:{order_number}")))
    return builder.as_markup()


def kb_balance_confirm(order_number: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("confirm", callback_data=f"pay:confirm_balance:{order_number}")))
    builder.row(InlineKeyboardButton(**btn("back", callback_data=f"pay:back:{order_number}")))
    return builder.as_markup()


def kb_order_confirmed():
    builder = InlineKeyboardBuilder()
    if settings.SUPPORT_BOT_URL:
        builder.row(InlineKeyboardButton(**btn("support", url=settings.SUPPORT_BOT_URL)))
    builder.row(back_btn("back_to_main", "menu:main"))
    return builder.as_markup()


def kb_card_payment(order_number: str, *, back_callback: str | None = None):
    builder = InlineKeyboardBuilder()
    if settings.SUPPORT_BOT_URL:
        builder.row(InlineKeyboardButton(**btn("support", url=settings.SUPPORT_BOT_URL)))
    builder.row(InlineKeyboardButton(**btn("back", callback_data=back_callback or f"pay:back:{order_number}")))
    return builder.as_markup()


def kb_card_payment_with_card(
    order_number: str,
    *,
    send_check_callback: str | None = None,
    back_callback: str | None = None,
):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("send_check", callback_data=send_check_callback or f"pay:send_check:{order_number}")))
    if settings.SUPPORT_BOT_URL:
        builder.row(InlineKeyboardButton(**btn("support", url=settings.SUPPORT_BOT_URL)))
    builder.row(InlineKeyboardButton(**btn("back", callback_data=back_callback or f"pay:back:{order_number}")))
    return builder.as_markup()


def kb_check_prompt(order_number: str, *, back_callback: str | None = None):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(**btn("back", callback_data=back_callback or f"pay:card:{order_number}")))
    return builder.as_markup()

