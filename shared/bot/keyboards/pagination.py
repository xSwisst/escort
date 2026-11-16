from __future__ import annotations

from aiogram.types import InlineKeyboardButton


def build_pagination_row(current: int, total: int, prefix: str) -> list[InlineKeyboardButton]:
    def _make(page: int, text: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=text, callback_data=f"{prefix}:{page}")

    def _page(page: int) -> InlineKeyboardButton:
        return _make(page, f"· {page} ·" if page == current else str(page))

    if total <= 1:
        return []
    if total <= 5:
        return [_page(page) for page in range(1, total + 1)]
    if current <= 3:
        return [_page(1), _page(2), _page(3), _make(4, "4 ›"), _make(total, f"{total} »")]
    if current >= total - 2:
        return [
            _make(1, "« 1"),
            _make(total - 3, f"‹ {total - 3}"),
            _page(total - 2),
            _page(total - 1),
            _page(total),
        ]
    return [
        _make(1, "« 1"),
        _make(current - 1, f"‹ {current - 1}"),
        _page(current),
        _make(current + 1, f"{current + 1} ›"),
        _make(total, f"{total} »"),
    ]
