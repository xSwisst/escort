from __future__ import annotations

from datetime import datetime, timedelta, timezone

MSK_TZ = timezone(timedelta(hours=3))

MONTHS_RU = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def format_datetime_ru(dt: datetime | str | None) -> str:
    """
    Форматирует дату и время в человекопонятный русский формат по МСК:
    '20 сентября 2026, в 12:52'
    """
    if not dt:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc).astimezone(MSK_TZ)
    else:
        dt = dt.astimezone(MSK_TZ)

    day = dt.day
    month_name = MONTHS_RU.get(dt.month, "")
    year = dt.year
    time_str = dt.strftime("%H:%M")
    return f"{day} {month_name} {year}, в {time_str}"
