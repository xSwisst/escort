#!/usr/bin/env python3
"""
Import static forms from ./static_forms/*.json into PostgreSQL (escort_db),
re-hosting every photo onto our `photos` service (http://photos:8005/internal/v1/files)
and randomly distributing 20-30 forms per city across 40 cities.
Supports --reset and --clean-only to remove previously imported static forms.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import secrets
import string
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy import delete, select

ROOT_DIR = Path(__file__).resolve().parent
for _p in (str(ROOT_DIR), str(ROOT_DIR / "shared")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from repository.models.cities import City
from repository.models.forms import Form, FormPhoto, FormPricing, FormProfile, FormPublication
from repository.repositories.cities import CityRepository
from repository.session import Database
from shared.auth import create_service_token

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

DOWNLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


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


def _load_photos_secret() -> str:
    if env_secret := os.getenv("PHOTOS_SECRET_KEY"):
        return env_secret
    photos_env = ROOT_DIR / "photos" / ".env"
    if photos_env.exists():
        for line in photos_env.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("API_SECRET_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
    if api_secret := os.getenv("API_SECRET_KEY"):
        return api_secret
    return "change-me-use-openssl-rand-hex-32"


async def _resolve_photos_url(configured_url: str) -> str:
    candidates = []
    if configured_url and configured_url.startswith("http://photos:"):
        candidates.append(configured_url)
    else:
        candidates.append("http://photos:8005")
        if configured_url:
            candidates.append(configured_url)

    async with httpx.AsyncClient(timeout=3.0) as client:
        for url in candidates:
            try:
                r = await client.get(f"{url.rstrip('/')}/health")
                if r.status_code == 200:
                    return url.rstrip("/")
            except Exception:
                continue
    return (configured_url or "http://photos:8005").rstrip("/")


async def rehost_photo(
    http_client: httpx.AsyncClient,
    source_url: str,
    *,
    photos_url: str,
    auth_token: str,
    errors: list[str] | None = None,
) -> str | None:
    try:
        dl = await http_client.get(source_url, headers=DOWNLOAD_HEADERS, follow_redirects=True)
        if dl.status_code != 200 or not dl.content:
            if errors is not None and len(errors) < 5:
                errors.append(f"download {dl.status_code}: {source_url}")
            return None
        ctype = (dl.headers.get("content-type") or "image/jpeg").split(";")[0].strip().lower()
        if ctype not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
            ctype = "image/jpeg"
        ext = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}.get(ctype, ".jpg")
        upload_resp = await http_client.post(
            f"{photos_url.rstrip('/')}/internal/v1/files",
            params={"category": "models"},
            headers={"Authorization": f"Bearer {auth_token}"},
            files={"file": (f"static{ext}", dl.content, ctype)},
        )
        if upload_resp.status_code != 200:
            if errors is not None and len(errors) < 5:
                errors.append(f"upload {upload_resp.status_code} ({photos_url}): {upload_resp.text[:160]}")
            return None
        payload = upload_resp.json()
        return payload.get("public_url") or payload.get("path")
    except Exception as exc:
        if errors is not None and len(errors) < 5:
            errors.append(f"exception ({source_url}): {exc}")
        return None


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


_PHOTO_FILE_RE = re.compile(r"^[a-f0-9]{64}\.(jpg|png|webp|gif)$")


def _extract_photo_filename(storage_key: str) -> str | None:
    path = urlparse(storage_key.strip()).path
    name = path.rsplit("/", 1)[-1]
    return name if _PHOTO_FILE_RE.fullmatch(name) else None


async def _delete_photos_from_service(
    storage_keys: list[str],
    *,
    photos_url: str,
) -> int:
    file_names = sorted({fn for k in storage_keys if (fn := _extract_photo_filename(k))})
    if not file_names:
        return 0

    secret_key = _load_photos_secret()
    audience = os.getenv("PHOTOS_AUDIENCE") or "photos_service"
    auth_token = create_service_token(secret_key=secret_key, issuer="api", audience=audience, ttl_hours=1)
    headers = {"Authorization": f"Bearer {auth_token}"}
    base = photos_url.rstrip("/")
    sem = asyncio.Semaphore(20)
    deleted_count = 0

    async with httpx.AsyncClient(timeout=15.0) as http_client:
        async def _del_one(fn: str) -> None:
            nonlocal deleted_count
            async with sem:
                try:
                    resp = await http_client.delete(f"{base}/internal/v1/files/{fn}", headers=headers)
                    if resp.status_code == 200:
                        deleted_count += 1
                except Exception:
                    pass

        await asyncio.gather(*(_del_one(fn) for fn in file_names))
    return deleted_count


async def clean_static_forms(db_url: str, *, photos_url: str) -> tuple[int, int]:
    db = Database(db_url)
    all_storage_keys: list[str] = []
    deleted_forms = 0
    try:
        async with db.session() as session:
            codes_stmt = select(FormPublication.form_code).where(FormPublication.is_static.is_(True))
            codes = list((await session.execute(codes_stmt)).scalars().all())
            if not codes:
                return 0, 0
            for i in range(0, len(codes), 500):
                batch = codes[i : i + 500]
                keys_stmt = select(FormPhoto.storage_key).where(FormPhoto.form_code.in_(batch))
                all_storage_keys.extend((await session.execute(keys_stmt)).scalars().all())
                await session.execute(delete(Form).where(Form.code.in_(batch)))
            await session.commit()
            deleted_forms = len(codes)
    finally:
        await db.close()

    deleted_photos = await _delete_photos_from_service(all_storage_keys, photos_url=photos_url)
    return deleted_forms, deleted_photos


async def import_forms(
    db_url: str,
    items: list[dict[str, Any]],
    city_names: list[str],
    *,
    photos_url: str,
    batch_size: int = 25,
) -> int:
    total = len(items)
    if total == 0:
        print("Нет анкет для импорта в static_forms/*.json")
        return 0

    secret_key = _load_photos_secret()
    audience = os.getenv("PHOTOS_AUDIENCE") or "photos_service"
    auth_token = create_service_token(secret_key=secret_key, issuer="api", audience=audience, ttl_hours=2)

    db = Database(db_url)
    saved = 0
    try:
        async with httpx.AsyncClient(timeout=25.0) as http_client:
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
                rehost_errors: list[str] = []

                for idx, item in enumerate(shuffled_items, start=1):
                    raw_photos = [str(p).strip() for p in (item.get("photos") or []) if str(p).strip()]
                    if not raw_photos:
                        render_progress(idx, total)
                        continue

                    uploaded_keys: list[str] = []
                    for src_url in raw_photos[:10]:
                        hosted = await rehost_photo(
                            http_client,
                            src_url,
                            photos_url=photos_url,
                            auth_token=auth_token,
                            errors=rehost_errors,
                        )
                        if hosted and hosted not in uploaded_keys:
                            uploaded_keys.append(hosted)

                    if not uploaded_keys:
                        if idx >= 5 and saved == 0:
                            sys.stdout.write("\n")
                            print("ОШИБКА: первые 5 анкет не смогли загрузить фото в photos! Примеры ошибок:")
                            for err in rehost_errors:
                                print("  -", err)
                            return 0
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
                            city_slot=1,
                            city_id=target_city.id,
                            is_static=True,
                            is_visible=True,
                            is_verified=True,
                            has_medical_certificate=True,
                            sort_order=per_city_order[target_city.id],
                        )
                    )
                    for order_idx, storage_key in enumerate(uploaded_keys):
                        session.add(
                            FormPhoto(
                                form_code=code,
                                storage_key=storage_key[:512],
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
    parser.add_argument("--no-clean", action="store_true", help="Do NOT delete existing static forms before importing")
    parser.add_argument("--clean-only", action="store_true", help="Delete all existing static forms and exit")
    parser.add_argument("--photos-url", default=None, help="Override photos service URL")
    parser.add_argument("--dry-run", action="store_true", help="Validate JSON and show progress without DB writes")
    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL") or "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    configured_photos_url = args.photos_url or os.getenv("PHOTOS_API_URL") or "http://photos:8005"
    photos_url = configured_photos_url if args.dry_run else await _resolve_photos_url(configured_photos_url)

    if args.clean_only:
        deleted_forms, deleted_photos = await clean_static_forms(db_url, photos_url=photos_url)
        print(f"Удалено статических анкет: {deleted_forms} | Удалено фото из photos: {deleted_photos}")
        return

    items = load_static_forms(Path(args.dir), limit=args.limit)
    print(f"Найдено анкет: {len(items)} | Городов: {len(DEFAULT_CITIES)} | Хостинг фото: {photos_url}")
    if not items:
        return

    if args.dry_run:
        for i in range(1, len(items) + 1):
            render_progress(i, len(items))
        print("Dry-run завершён (20-30 анкет на город, фото будут загружены в photos).")
        return

    if not args.no_clean:
        deleted_forms, deleted_photos = await clean_static_forms(db_url, photos_url=photos_url)
        print(f"Удалено старых статических анкет: {deleted_forms} | Удалено старых фото: {deleted_photos}")

    saved = await import_forms(db_url, items, DEFAULT_CITIES, photos_url=photos_url)
    print(f"Готово! Загружено в БД: {saved} (фото перекачаны на наш хостинг)")


if __name__ == "__main__":
    asyncio.run(async_main())
