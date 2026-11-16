from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn, t
from bot.keyboards.common import back_btn, nav_buttons
from core.settings import settings

MODELS_PER_PAGE = 9

def kb_models_list(forms: list, page: int, per_page: int | None = None):
    per_page = MODELS_PER_PAGE
    total_pages = max(1, (len(forms) + per_page - 1) // per_page)
    start = page * per_page
    page_forms = forms[start:start + per_page]

    builder = InlineKeyboardBuilder()
    for i, form in enumerate(page_forms):
        builder.row(InlineKeyboardButton(text=t("models_list_item", index=start + i + 1, name=form.name, age=form.age), callback_data=f"model:view:{form.code}"))

    navigation = nav_buttons(page + 1, total_pages, "models")
    if navigation:
        builder.row(*navigation)
    builder.row(back_btn("back_to_main", "menu:main"))
    return builder.as_markup()


def kb_model_card(
    form_code: str,
    is_favorite: bool = False,
    has_reviews: bool = False,
    has_services: bool = False,
    has_additionals: bool = False,
    blog_url: str | None = None,
    has_private_channel: bool = False,
    order_available: bool = True,
    back_target: str = "menu:models",
):
    builder = InlineKeyboardBuilder()
    if order_available:
        builder.row(InlineKeyboardButton(**btn("order", callback_data=f"model:order:{form_code}")))


    media_row = [InlineKeyboardButton(**btn("other_photo", callback_data=f"model:photo:{form_code}"))]
    if has_reviews:
        media_row.append(InlineKeyboardButton(**btn("view_reviews", callback_data=f"model:reviews:{form_code}")))
    builder.row(*media_row)

    info_row = []
    if has_services:
        info_row.append(InlineKeyboardButton(**btn("services", callback_data=f"model:services:{form_code}")))
    if has_additionals:
        info_row.append(InlineKeyboardButton(**btn("additionals", callback_data=f"model:additionals:{form_code}")))
    if info_row:
        builder.row(*info_row)

    channel_row = []
    if blog_url:
        channel_row.append(InlineKeyboardButton(**btn("blog", url=blog_url)))
    if has_private_channel:
        channel_row.append(InlineKeyboardButton(**btn("private_channel", callback_data=f"model:private:{form_code}")))
    if channel_row:
        builder.row(*channel_row)

    favorite_key = "in_favorites" if is_favorite else "to_favorites"
    builder.row(InlineKeyboardButton(**btn(favorite_key, callback_data=f"model:fav:{form_code}")))
    if back_target == "menu:profile":
        builder.row(back_btn("back_to_profile", "menu:profile"))
    else:
        builder.row(back_btn("back_to_models", "menu:models"))
    return builder.as_markup()


def kb_reviews(form_code: str, *, page: int = 1, total_pages: int = 1):
    builder = InlineKeyboardBuilder()
    navigation = nav_buttons(page, total_pages, f"model:reviews-page:{form_code}")
    if navigation:
        builder.row(*navigation)
    builder.row(back_btn("back_to_model", f"model:view:{form_code}"))
    return builder.as_markup()


def kb_additionals_view(form_code: str):
    builder = InlineKeyboardBuilder()
    builder.row(back_btn("back_to_model", f"model:view:{form_code}"))
    return builder.as_markup()


def kb_services_view(form_code: str):
    builder = InlineKeyboardBuilder()
    builder.row(back_btn("back_to_model", f"model:view:{form_code}"))
    return builder.as_markup()


def kb_private_channel_view(form_code: str, *, payment_available: bool = False):
    builder = InlineKeyboardBuilder()
    if payment_available:
        builder.row(InlineKeyboardButton(**btn("pay_card", callback_data=f"pchan:method:{form_code}:card")))
    builder.row(back_btn("back_to_model", f"model:view:{form_code}"))
    return builder.as_markup()

