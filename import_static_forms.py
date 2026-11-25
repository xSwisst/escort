#!/usr/bin/env python3
"""
Import static forms from ./static_forms/*.json into PostgreSQL (escort_db).
Includes a terminal progress bar and automatic price generation.
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

ROOT_DIR = Path(__file__).resolve().parent
for _p in (str(ROOT_DIR), str(ROOT_DIR / "shared")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from repository.models.forms import Form, FormPhoto, FormPricing, FormProfile, FormPublication
from repository.session import Database


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


async def import_forms(db_url: str, items: list[dict[str, Any]], *, batch_size: int = 50) -> int:
    total = len(items)
    if total == 0:
        print("Нет анкет для импорта в static_forms/*.json")
        return 0

    db = Database(db_url)
    saved = 0
    try:
        async with db.session() as session:
            for idx, item in enumerate(items, start=1):
                photos = [str(p).strip() for p in (item.get("photos") or []) if str(p).strip()]
                if not photos:
                    render_progress(idx, total)
                    continue

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
                        city_id=None,
                        is_static=True,
                        is_visible=True,
                        is_verified=True,
                        has_medical_certificate=True,
                        sort_order=idx,
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
    parser.add_argument("--dry-run", action="store_true", help="Validate JSON and show progress without DB writes")
    args = parser.parse_args()

    items = load_static_forms(Path(args.dir), limit=args.limit)
    print(f"Найдено анкет: {len(items)}")
    if not items:
        return

    if args.dry_run:
        for i in range(1, len(items) + 1):
            render_progress(i, len(items))
        print("Dry-run завершён.")
        return

    db_url = os.getenv("DATABASE_URL") or "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    saved = await import_forms(db_url, items)
    print(f"Готово! Загружено в БД: {saved}")


if __name__ == "__main__":
    asyncio.run(async_main())
