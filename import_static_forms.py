#!/usr/bin/env python3
"""
Import static forms from ./static_forms/*.json into PostgreSQL (escort_db),
evenly distributed across 40 cities (~25 forms per city).
Supports --reset and --clean-only to remove previously imported static forms.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import secrets
import string
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select

ROOT_DIR = Path(__file__).resolve().parent
for _p in (str(ROOT_DIR), str(ROOT_DIR / "shared")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from repository.models.cities import City
from repository.models.forms import Form, FormPhoto, FormPricing, FormProfile, FormPublication
from repository.repositories.cities import CityRepository
from repository.session import Database

DEFAULT_CITIES: list[str] = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Ростов-на-Дону",
    "Уфа",
    "Красноярск",
    "Воронеж",
    "Пермь",
    "Волгоград",
    "Краснодар",
    "Саратов",
    "Тюмень",
    "Тольятти",
    "Ижевск",
    "Барнаул",
    "Ульяновск",
    "Иркутск",
    "Хабаровск",
    "Ярославль",
    "Владивосток",
    "Махачкала",
    "Томск",
    "Оренбург",
    "Кемерово",
    "Новокузнецк",
    "Рязань",
    "Астрахань",
    "Набережные Челны",
    "Пенза",
    "Липецк",
    "Киров",
    "Чебоксары",
    "Калининград",
    "Сочи",
]


def _round_500(value: float) -> int:
    return int(round(value / 500.0) * 500)


def generate_prices() -> dict[str, int]:
    p1 = random.randrange(4000, 7001, 500)
    p2 = _round_500(p1 * random.uniform(1.70, 1.90))
    p3 = _round_500(p1 * random.uniform(2.50, 2.60))
    p_night = _round_500(p1 * random.uniform(5.50, 7.00))
    return {
        "one_hour_price": p1,
        "two_hour_price": p2,
        "three_hour_price": p3,
        "overnight_price": p_night,
    }


def _generate_code(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def render_progress(current: int, total: int, *, width: int = 32) -> None:
    if total <= 0:
        return
    ratio = min(1.0, max(0.0, current / total))
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(ratio * 100)
    sys.stdout.write(f"\r[{bar}] {percent:3d}% ({current}/{total})")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()


def load_static_forms(static_dir: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    if not static_dir.exists():
        raise FileNotFoundError(f"Directory not found: {static_dir}")

    items: list[dict[str, Any]] = []
    for json_path in sorted(static_dir.glob("*.json")):
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            items.extend(x for x in raw if isinstance(x, dict))
        elif isinstance(raw, dict) and isinstance(raw.get("items"), list):
            items.extend(x for x in raw["items"] if isinstance(x, dict))

    if limit is not None and limit > 0:
        items = items[:limit]
    return items


async def clean_static_forms(db_url: str) -> int:
    db = Database(db_url)
    try:
        async with db.session() as session:
            codes_stmt = select(FormPublication.form_code).where(FormPublication.is_static.is_(True))
            codes = list((await session.execute(codes_stmt)).scalars().all())
            if not codes:
                return 0
            # Delete in batches to keep query size bounded
            for i in range(0, len(codes), 500):
                batch = codes[i : i + 500]
                await session.execute(delete(Form).where(Form.code.in_(batch)))
            await session.commit()
            return len(codes)
    finally:
        await db.close()


async def import_forms(
    db_url: str,
    items: list[dict[str, Any]],
    city_names: list[str],
    *,
    batch_size: int = 50,
) -> int:
    total = len(items)
    if total == 0:
        print("Нет анкет для импорта в static_forms/*.json")
        return 0

    db = Database(db_url)
    saved = 0
    try:
        async with db.session() as session:
            city_repo = CityRepository(session)
            cities: list[City] = []
            for cname in city_names:
                city = await city_repo.get_by_name(cname)
                if city is None:
                    city = City(name=cname.strip())
                    session.add(city)
                    await session.flush()
                    await session.refresh(city)
                cities.append(city)

            city_counts = [random.randint(20, 30) for _ in cities]
            city_assignments: list[City] = []
            for city_obj, count in zip(cities, city_counts):
                city_assignments.extend([city_obj] * count)
            while len(city_assignments) < total:
                city_assignments.append(random.choice(cities))

            shuffled_items = list(items)
            random.shuffle(shuffled_items)
            per_city_order: dict[int, int] = {}

            for idx, item in enumerate(shuffled_items, start=1):
                photos = [str(p).strip() for p in (item.get("photos") or []) if str(p).strip()]
                if not photos:
                    render_progress(idx, total)
                    continue

                target_city = city_assignments[idx - 1]
                per_city_order[target_city.id] = per_city_order.get(target_city.id, 0) + 1
                code = _generate_code()
                prices = generate_prices()

                session.add(Form(code=code, admin_id=None))
                await session.flush()

                session.add(
                    FormProfile(
                        form_code=code,
                        name=str(item.get("name") or "Модель")[:128],
                        age=int(item["age"]),
                        height=int(item["height"]),
                        weight=int(item["weight"]) if item.get("weight") is not None else None,
                        bust_size=int(item["bust_size"]),
                    )
                )
                session.add(FormPricing(form_code=code, **prices))
                session.add(
                    FormPublication(
                        form_code=code,
                        city_slot=2,
                        city_id=target_city.id,
                        is_static=True,
                        is_visible=True,
                        is_verified=True,
                        has_medical_certificate=True,
                        sort_order=per_city_order[target_city.id],
                    )
                )
                for order_idx, photo_url in enumerate(photos[:10]):
                    session.add(
                        FormPhoto(
                            form_code=code,
                            storage_key=photo_url[:512],
                            sort_order=order_idx,
                        )
                    )

                saved += 1
                if saved % batch_size == 0:
                    await session.commit()
                render_progress(idx, total)

            await session.commit()
    finally:
        await db.close()
    return saved


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Import static forms from ./static_forms into escort_db")
    parser.add_argument("--dir", default="static_forms", help="Directory with JSON files (default: static_forms)")
    parser.add_argument("--limit", type=int, default=None, help="Optional max forms to import")
    parser.add_argument("--reset", action="store_true", help="Delete all existing static forms before importing")
    parser.add_argument("--clean-only", action="store_true", help="Delete all existing static forms and exit")
    parser.add_argument("--dry-run", action="store_true", help="Validate JSON and show progress without DB writes")
    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL") or "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"

    if args.clean_only:
        deleted = await clean_static_forms(db_url)
        print(f"Удалено статических анкет: {deleted}")
        return

    items = load_static_forms(Path(args.dir), limit=args.limit)
    print(f"Найдено анкет: {len(items)} | Городов: {len(DEFAULT_CITIES)}")
    if not items:
        return

    if args.dry_run:
        for i in range(1, len(items) + 1):
            render_progress(i, len(items))
        print(f"Dry-run завершён (~{len(items) // len(DEFAULT_CITIES)} анкет на город).")
        return

    if args.reset:
        deleted = await clean_static_forms(db_url)
        print(f"Удалено старых статических анкет: {deleted}")

    saved = await import_forms(db_url, items, DEFAULT_CITIES)
    print(f"Готово! Загружено в БД: {saved} (распределено по {len(DEFAULT_CITIES)} городам)")


if __name__ == "__main__":
    asyncio.run(async_main())
