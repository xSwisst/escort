from __future__ import annotations

try:
    from aiogram.types import CopyTextButton
except ImportError:
    CopyTextButton = None  # type: ignore

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn, nav_buttons


def kb_malling_audience() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**btn("va_malling_all_clients", callback_data="admin:malling:aud:all"))],
            [InlineKeyboardButton(**btn("va_malling_new_7d", callback_data="admin:malling:aud:new7"))],
            [InlineKeyboardButton(**btn("va_malling_new_14d", callback_data="admin:malling:aud:new14"))],
            [InlineKeyboardButton(**btn("va_malling_new_30d", callback_data="admin:malling:aud:new30"))],
            [back_btn("admin:panel")],
        ]
    )


def kb_malling_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**btn("preview", callback_data="admin:malling:preview"))],
            [
                InlineKeyboardButton(**btn("add_media", callback_data="admin:malling:media:add")),
                InlineKeyboardButton(**btn("buttons", callback_data="admin:malling:buttons")),
            ],
            [InlineKeyboardButton(**btn("confirm_send", callback_data="admin:malling:send"))],
            [back_btn("admin:malling:cancel")],
        ]
    )


def kb_malling_back_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn("admin:malling:settings")]])


def kb_malling_cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn("admin:malling:cancel")]])


def kb_malling_media_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**btn("confirm", callback_data="admin:malling:media:confirm"))],
            [back_btn("admin:malling:settings")],
        ]
    )


def kb_malling_button_type() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**btn("button_type_url", callback_data="admin:malling:btn:type:url"))],
            [InlineKeyboardButton(**btn("button_type_callback", callback_data="admin:malling:btn:type:callback"))],
            [InlineKeyboardButton(**btn("button_type_copy", callback_data="admin:malling:btn:type:copy"))],
            [back_btn("admin:malling:settings")],
        ]
    )


def kb_malling_button_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**btn("confirm", callback_data="admin:malling:btn:add:confirm"))],
            [back_btn("admin:malling:settings")],
        ]
    )


def kb_malling_button_view(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**btn("delete", callback_data=f"admin:malling:btn:del:{index}"))],
            [back_btn("admin:malling:buttons")],
        ]
    )


def kb_malling_button_delete_confirm(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**btn("confirm", callback_data=f"admin:malling:btn:del:confirm:{index}"))],
            [back_btn(f"admin:malling:btn:view:{index}")],
        ]
    )


def kb_malling_buttons_list(buttons_data: list[dict], page: int = 1, per_page: int = 8) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    total = len(buttons_data)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    end = start + per_page
    for idx in range(start, min(end, total)):
        button = buttons_data[idx]
        text = button.get("text", "—")
        builder.row(InlineKeyboardButton(**btn("row_info", text=text, callback_data=f"admin:malling:btn:view:{idx}")))
    builder.row(InlineKeyboardButton(**btn("add", callback_data="admin:malling:btn:add")))
    nav = nav_buttons(page, pages, "admin:malling:buttons:page")
    if nav:
        builder.row(*nav)
    builder.row(back_btn("admin:malling:settings"))
    return builder.as_markup()


def kb_malling_hide() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(**btn("hide", callback_data="admin:malling:hide"))]]
    )


def build_malling_inline_keyboard(buttons_data: list[dict]) -> InlineKeyboardMarkup | None:
    if not buttons_data:
        return None
    builder = InlineKeyboardBuilder()
    for item in buttons_data:
        btype = (item.get("type") or "").lower()
        text = item.get("text", "—")
        if btype == "url" and item.get("url"):
            builder.row(InlineKeyboardButton(text=text, url=item["url"]))
        elif btype == "copy" and item.get("copy_text"):
            if CopyTextButton is not None:
                try:
                    builder.row(InlineKeyboardButton(text=text, copy_text=CopyTextButton(text=item["copy_text"])))
                except Exception:
                    builder.row(InlineKeyboardButton(text=text, callback_data="noop"))
            else:
                builder.row(InlineKeyboardButton(text=text, callback_data="noop"))
        elif btype == "callback" and item.get("callback_data"):
            builder.row(InlineKeyboardButton(text=text, callback_data=item["callback_data"][:64]))
    markup = builder.as_markup()
    return markup if markup.inline_keyboard else None



