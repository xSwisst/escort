from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.assets.texts import btn
from bot.keyboards.common import back_btn, nav_buttons


def kb_models_list(
    forms: list,
    city_slot: int,
    page: int = 1,
    per_page: int = 5,
) -> InlineKeyboardMarkup:
    rows = []
    total = len(forms)
    total_pages = max(1, -(-total // per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    chunk = forms[start : start + per_page]

    for idx, f in enumerate(chunk, start=start + 1):
        name = getattr(f, "name", f.get("name") if isinstance(f, dict) else "—")
        age = getattr(f, "age", f.get("age") if isinstance(f, dict) else "")
        code = getattr(f, "code", f.get("code") if isinstance(f, dict) else "")
        rows.append([InlineKeyboardButton(text=f"#{idx} | {name}, {age}", callback_data=f"admin:form:info:{code}")])

    rows.append([InlineKeyboardButton(**btn("worker_positions", callback_data=f"admin:forms:positions:{city_slot}:1"))])
    rows.append([InlineKeyboardButton(**btn("add", callback_data=f"admin:forms:new:{city_slot}"))])
    nav = nav_buttons(page, total_pages, f"admin:forms:city:{city_slot}")
    if nav:
        rows.append(nav)
    rows.append([back_btn("admin:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_model_card(form, city_slot: int) -> InlineKeyboardMarkup:
    code = getattr(form, "code", form.get("code") if isinstance(form, dict) else "")
    is_visible = getattr(form, "is_visible", form.get("is_visible", True) if isinstance(form, dict) else True)
    rows = [
        # Row 1 — two buttons
        [
            InlineKeyboardButton(text="⭐️ Рейтинг", callback_data=f"admin:form:param:{code}:rating"),
            InlineKeyboardButton(text="✏️ Описание", callback_data=f"admin:form:param:{code}:caption"),
        ],
        # Row 2 — two buttons
        [
            InlineKeyboardButton(text="📋 Заказы", callback_data=f"admin:form:param:{code}:orders"),
            InlineKeyboardButton(text="✈️ Канал", callback_data=f"admin:form:param:{code}:channel"),
        ],
        # Row 3
        [InlineKeyboardButton(text=btn("edit_form")["text"], callback_data=f"admin:form:edit:{code}")],
        # Row 4
        [InlineKeyboardButton(text=btn("manage_reviews")["text"], callback_data=f"admin:form:reviews:{code}:1")],
        # Row 5 — two buttons
        [
            InlineKeyboardButton(text=btn("manage_services_short")["text"], callback_data=f"admin:form:services:{code}:1"),
            InlineKeyboardButton(text=btn("manage_additionals_short")["text"], callback_data=f"admin:form:additionals:{code}:1"),
        ],
        # Row 6 — two buttons
        [
            InlineKeyboardButton(text=btn("toggle_verification")["text"], callback_data=f"admin:form:toggle:{code}:is_verified"),
            InlineKeyboardButton(text=btn("toggle_document")["text"], callback_data=f"admin:form:toggle:{code}:has_medical_certificate"),
        ],
        # Row 7 — two buttons
        [
            InlineKeyboardButton(text=btn("toggle_dynamic")["text"], callback_data="admin:noop"),
            InlineKeyboardButton(text=btn("toggle_show" if is_visible else "toggle_hide")["text"], callback_data=f"admin:form:toggle:{code}:is_visible"),
        ],
        # Row 8
        [InlineKeyboardButton(text=btn("manage_photos")["text"], callback_data=f"admin:form:photos:{code}:0")],
        # Row 10
        [InlineKeyboardButton(**btn("delete", callback_data=f"admin:form:del:{code}"))],
        # Row 11 — back
        [back_btn(f"admin:forms:city:{city_slot}:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_edit_params(code: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text=btn("edit_default_name")["text"], callback_data=f"admin:form:param:{code}:name"),
            InlineKeyboardButton(text=btn("edit_default_age")["text"], callback_data=f"admin:form:param:{code}:age"),
        ],
        [
            InlineKeyboardButton(text=btn("edit_default_height")["text"], callback_data=f"admin:form:param:{code}:height"),
            InlineKeyboardButton(text=btn("edit_default_tits")["text"], callback_data=f"admin:form:param:{code}:bust_size"),
        ],
        [
            InlineKeyboardButton(text=btn("edit_default_price1")["text"], callback_data=f"admin:form:param:{code}:one_hour_price"),
            InlineKeyboardButton(text=btn("edit_default_price_two_hours")["text"], callback_data=f"admin:form:param:{code}:two_hour_price"),
        ],
        [
            InlineKeyboardButton(text=btn("edit_default_price2")["text"], callback_data=f"admin:form:param:{code}:three_hour_price"),
            InlineKeyboardButton(text=btn("edit_default_price3")["text"], callback_data=f"admin:form:param:{code}:overnight_price"),
        ],
        [back_btn(f"admin:form:info:{code}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_param_input(code: str, param: str, can_delete: bool = False, back_target: str = "") -> InlineKeyboardMarkup:
    rows = []
    if can_delete:
        rows.append([InlineKeyboardButton(**btn("delete", callback_data=f"admin:form:param-del-ask:{code}:{param}"))])
    rows.append([back_btn(back_target or f"admin:form:info:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_param_confirm_update(code: str, param: str, back_target: str = "") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data=f"admin:form:param-approve:{code}:{param}"))],
        [back_btn(back_target or f"admin:form:param:{code}:{param}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_param_confirm_delete(code: str, param: str, back_target: str = "") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data=f"admin:form:param-del-approve:{code}:{param}"))],
        [back_btn(back_target or f"admin:form:param:{code}:{param}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_form_photos(code: str, count: int, current: int) -> InlineKeyboardMarkup:
    rows = []
    if count > 0:
        rows.append([InlineKeyboardButton(text=btn("photos_delete_current")["text"], callback_data=f"admin:form:photo:del:{code}:{current}")])
    if count > 1:
        prev_idx = (current - 1) % count
        next_idx = (current + 1) % count
        rows.append([
            InlineKeyboardButton(text="◀️", callback_data=f"admin:form:photos:{code}:{prev_idx}"),
            InlineKeyboardButton(text=f"{current + 1}/{count}", callback_data="admin:noop"),
            InlineKeyboardButton(text="▶️", callback_data=f"admin:form:photos:{code}:{next_idx}"),
        ])
    rows.append([InlineKeyboardButton(text=btn("photos_add")["text"], callback_data=f"admin:form:photo:add:{code}")])
    rows.append([back_btn(f"admin:form:info:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_reviews_list(code: str, reviews: list, page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    rows = []
    total = len(reviews)
    total_pages = max(1, -(-total // per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    chunk = reviews[start : start + per_page]

    for rv in chunk:
        rid = getattr(rv, "id", rv.get("id") if isinstance(rv, dict) else "")
        author = getattr(rv, "author", rv.get("author") if isinstance(rv, dict) else "—")
        rows.append([InlineKeyboardButton(text=f"#{rid} | {author}", callback_data=f"admin:form:review:info:{code}:{rid}")])

    rows.append([InlineKeyboardButton(**btn("new_review", callback_data=f"admin:form:review:add:{code}"))])
    nav = nav_buttons(page, total_pages, f"admin:form:reviews:{code}")
    if nav:
        rows.append(nav)
    rows.append([back_btn(f"admin:form:info:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_review_card(code: str, review_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("delete", callback_data=f"admin:form:review:del:{code}:{review_id}"))],
        [back_btn(f"admin:form:reviews:{code}:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_services_list(code: str, services: list, page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    rows = []
    total = len(services)
    total_pages = max(1, -(-total // per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    chunk = services[start : start + per_page]

    for item in chunk:
        sid = getattr(item, "id", item.get("id") if isinstance(item, dict) else "")
        name = getattr(item, "name", item.get("name") if isinstance(item, dict) else "—")
        rows.append([InlineKeyboardButton(text=f"#{sid} | {name}", callback_data=f"admin:form:service:info:{code}:{sid}")])

    rows.append([InlineKeyboardButton(**btn("new_service", callback_data=f"admin:form:service:add:{code}"))])
    nav = nav_buttons(page, total_pages, f"admin:form:services:{code}")
    if nav:
        rows.append(nav)
    rows.append([back_btn(f"admin:form:info:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_service_card(code: str, service_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("delete", callback_data=f"admin:form:service:del:{code}:{service_id}"))],
        [back_btn(f"admin:form:services:{code}:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_additionals_list(code: str, additionals: list, page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    rows = []
    total = len(additionals)
    total_pages = max(1, -(-total // per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    chunk = additionals[start : start + per_page]

    for item in chunk:
        aid = getattr(item, "id", item.get("id") if isinstance(item, dict) else "")
        name = getattr(item, "name", item.get("name") if isinstance(item, dict) else "—")
        price = getattr(item, "price", item.get("price") if isinstance(item, dict) else 0)
        rows.append([InlineKeyboardButton(text=f"#{aid} | {name} ({price} RUB)", callback_data=f"admin:form:additional:info:{code}:{aid}")])

    rows.append([InlineKeyboardButton(**btn("new_additional", callback_data=f"admin:form:additional:add:{code}"))])
    nav = nav_buttons(page, total_pages, f"admin:form:additionals:{code}")
    if nav:
        rows.append(nav)
    rows.append([back_btn(f"admin:form:info:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_additional_card(code: str, additional_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("delete", callback_data=f"admin:form:additional:del:{code}:{additional_id}"))],
        [back_btn(f"admin:form:additionals:{code}:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_positions(forms: list, city_slot: int, page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    rows = []
    total = len(forms)
    start = (page - 1) * per_page
    chunk = forms[start : start + per_page]

    for i, f in enumerate(chunk):
        code = getattr(f, "code", f.get("code") if isinstance(f, dict) else "")
        name = getattr(f, "name", f.get("name") if isinstance(f, dict) else "—")
        age = getattr(f, "age", f.get("age") if isinstance(f, dict) else "—")
        global_idx = start + i
        up_cb = f"admin:form:pos-up:{city_slot}:{code}" if global_idx > 0 else "admin:noop"
        down_cb = f"admin:form:pos-down:{city_slot}:{code}" if global_idx < total - 1 else "admin:noop"
        rows.append(
            [
                InlineKeyboardButton(text=f"#{global_idx + 1} | {name}, {age}", callback_data="admin:noop"),
                InlineKeyboardButton(text="⬆️", callback_data=up_cb),
                InlineKeyboardButton(text="⬇️", callback_data=down_cb),
            ]
        )

    total_pages = max(1, -(-total // per_page))
    nav = nav_buttons(page, total_pages, f"admin:forms:positions:{city_slot}")
    if nav:
        rows.append(nav)

    rows.append([back_btn(f"admin:forms:city:{city_slot}:1")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_confirm_delete_model(code: str, city_slot: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data=f"admin:form:del:confirm:{code}"))],
        [back_btn(f"admin:form:info:{code}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_approve_new_model(city_slot: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(**btn("confirm", callback_data="admin:forms:new:approve"))],
        [back_btn(f"admin:forms:city:{city_slot}:1")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
