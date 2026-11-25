#!/usr/bin/env python3
"""
Static forms parser for https://buck.prostitutkigac.com/

Extracts ONLY:
- photos
- age
- height
- weight
- bust_size

Generates prices according to business rules:
- 1h: random 4000..7000 step 500
- 2h: +70..90%, rounded to 500
- 3h: +150..160%, rounded to 500
- night: +450..600%, rounded to 500
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import random
import re
import secrets
import string
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import httpx

ROOT_DIR = Path(__file__).resolve().parent
for _p in (str(ROOT_DIR), str(ROOT_DIR / "shared")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from repository.models.cities import City
from repository.models.forms import Form, FormPhoto, FormPricing, FormProfile, FormPublication
from repository.repositories.cities import CityRepository
from repository.session import Database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("parse_forms")

DEFAULT_BASE_URL = "https://buck.prostitutkigac.com/"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Adjust these patterns if the target site HTML structure differs.
PROFILE_LINK_RE = re.compile(r'href=["\']([^"\']*(?:anketa|model|girl|profile|prostitutk)[^"\']*?\d+[^"\']*)["\']', re.I)
NEXT_PAGE_RE = re.compile(
    r'<a[^>]+(?:rel=["\']next["\']|class=["\'][^"\']*next[^"\']*["\'])[^>]+href=["\']([^"\']+)["\']'
    r'|<a[^>]+href=["\']([^"\']+)["\'][^>]+(?:rel=["\']next["\']|class=["\'][^"\']*next[^"\']*["\'])',
    re.I,
)
PAGINATION_LINK_RE = re.compile(
    r'href=["\']([^"\']*(?:[?&]page=\d+|/page/\d+/?|[?&]PAGEN_\d+=\d+)[^"\']*)["\']',
    re.I,
)
IMAGE_SRC_RE = re.compile(r'(?:src|data-src|data-lazy|href)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)(?:\?[^"\']*)?)["\']', re.I)
AGE_RE = re.compile(r"(?:Возраст|Age)\s*[:\-]?\s*(\d{2})", re.I)
HEIGHT_RE = re.compile(r"(?:Рост|Height)\s*[:\-]?\s*(\d{3})", re.I)
WEIGHT_RE = re.compile(r"(?:Вес|Weight)\s*[:\-]?\s*(\d{2,3})", re.I)
BUST_RE = re.compile(r"(?:Грудь|Размер\s*груди|Бюст|Bust)\s*[:\-]?\s*(\d{1,2})", re.I)
NAME_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
TAG_STRIP_RE = re.compile(r"<[^>]+>")


@dataclass
class ParsedForm:
    name: str
    age: int
    height: int
    weight: int | None
    bust_size: int
    photos: list[str] = field(default_factory=list)


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


def parse_profile_html(html: str, base_url: str) -> ParsedForm | None:
    plain = TAG_STRIP_RE.sub(" ", html)
    plain = re.sub(r"\s+", " ", plain)

    age_m = AGE_RE.search(plain)
    height_m = HEIGHT_RE.search(plain)
    bust_m = BUST_RE.search(plain)
    if not (age_m and height_m and bust_m):
        return None

    weight_m = WEIGHT_RE.search(plain)
    name_m = NAME_RE.search(html)
    raw_name = TAG_STRIP_RE.sub("", name_m.group(1)).strip() if name_m else ""
    name = raw_name.split(",")[0].strip()[:120] or "Модель"

    photos: list[str] = []
    seen: set[str] = set()
    for m in IMAGE_SRC_RE.finditer(html):
        url = urljoin(base_url, m.group(1).strip())
        lower = url.lower()
        if any(skip in lower for skip in ("logo", "icon", "favicon", "avatar", "banner", "sprite")):
            continue
        if url not in seen:
            seen.add(url)
            photos.append(url)
        if len(photos) >= 10:
            break

    if not photos:
        return None

    return ParsedForm(
        name=name,
        age=int(age_m.group(1)),
        height=int(height_m.group(1)),
        weight=int(weight_m.group(1)) if weight_m else None,
        bust_size=int(bust_m.group(1)),
        photos=photos,
    )


def extract_profile_urls(listing_html: str, base_url: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for m in PROFILE_LINK_RE.finditer(listing_html):
        full = urljoin(base_url, m.group(1).strip())
        if full not in seen:
            seen.add(full)
            urls.append(full)
    return urls


def extract_next_page_urls(listing_html: str, current_url: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for m in NEXT_PAGE_RE.finditer(listing_html):
        href = (m.group(1) or m.group(2) or "").strip()
        if href:
            full = urljoin(current_url, href)
            if full not in seen:
                seen.add(full)
                urls.append(full)
    for m in PAGINATION_LINK_RE.finditer(listing_html):
        href = m.group(1).strip()
        if href:
            full = urljoin(current_url, href)
            if full not in seen:
                seen.add(full)
                urls.append(full)
    return urls


async def fetch_text(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        resp = await client.get(url, headers=DEFAULT_HEADERS, follow_redirects=True)
        if resp.status_code == 200:
            return resp.text
        logger.warning("HTTP %s for %s", resp.status_code, url)
    except Exception as exc:
        logger.warning("Request error for %s: %s", url, exc)
    return None


async def collect_from_web(
    base_url: str,
    *,
    limit: int,
    max_pages: int,
    proxy: str | None,
    page_template: str | None = None,
) -> list[ParsedForm]:
    results: list[ParsedForm] = []
    client_kwargs: dict = {"timeout": 20.0}
    if proxy:
        client_kwargs["proxy"] = proxy

    async with httpx.AsyncClient(**client_kwargs) as client:
        profile_urls: list[str] = []
        seen_profiles: set[str] = set()
        visited_pages: set[str] = set()
        page_queue: list[str] = [base_url]
        page_num = 0

        while page_queue and page_num < max_pages and len(profile_urls) < limit:
            page_url = page_queue.pop(0)
            if page_url in visited_pages:
                continue
            visited_pages.add(page_url)
            page_num += 1

            html = await fetch_text(client, page_url)
            if not html:
                break

            found = extract_profile_urls(html, page_url)
            new_count = 0
            for u in found:
                if u not in seen_profiles:
                    seen_profiles.add(u)
                    profile_urls.append(u)
                    new_count += 1
            logger.info("Page %s (%s): +%s profiles (total=%s)", page_num, page_url, new_count, len(profile_urls))

            if page_template:
                next_url = page_template.format(page=page_num + 1, base=base_url.rstrip("/"))
                if next_url not in visited_pages:
                    page_queue.append(next_url)
            else:
                discovered = extract_next_page_urls(html, page_url)
                if discovered:
                    for next_url in discovered:
                        if next_url not in visited_pages and next_url not in page_queue:
                            page_queue.append(next_url)
                elif new_count > 0:
                    fallback = f"{base_url.rstrip('/')}/?page={page_num + 1}"
                    if fallback not in visited_pages:
                        page_queue.append(fallback)

        for idx, url in enumerate(profile_urls[:limit], start=1):
            html = await fetch_text(client, url)
            if not html:
                continue
            parsed = parse_profile_html(html, base_url)
            if parsed:
                results.append(parsed)
            if idx % 25 == 0:
                logger.info("Processed %s/%s profiles (parsed=%s)", idx, min(len(profile_urls), limit), len(results))
            await asyncio.sleep(0.1)

    return results


def collect_from_dir(html_dir: Path, base_url: str, *, limit: int) -> list[ParsedForm]:
    if not html_dir.exists():
        logger.warning("HTML directory does not exist: %s", html_dir)
        return []
    files = sorted(html_dir.rglob("*.html"))
    if not files:
        logger.warning("No .html files found in %s", html_dir)
        return []
    logger.info("Found %s .html files in %s", len(files), html_dir)

    results: list[ParsedForm] = []
    for path in files:
        if len(results) >= limit:
            break
        html = path.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_profile_html(html, base_url)
        if parsed:
            results.append(parsed)
    return results


async def save_forms(db_url: str, city_name: str | None, forms: list[ParsedForm]) -> int:
    db = Database(db_url)
    saved = 0
    try:
        async with db.session() as session:
            city_id: int | None = None
            if city_name:
                city_repo = CityRepository(session)
                city = await city_repo.get_by_name(city_name)
                if city is None:
                    city = City(name=city_name.strip())
                    session.add(city)
                    await session.flush()
                    await session.refresh(city)
                city_id = city.id

            for idx, item in enumerate(forms, start=1):
                code = _generate_code()
                prices = generate_prices()
                form = Form(code=code, admin_id=None)
                session.add(form)
                await session.flush()

                session.add(
                    FormProfile(
                        form_code=code,
                        name=item.name,
                        age=item.age,
                        height=item.height,
                        weight=item.weight,
                        bust_size=item.bust_size,
                    )
                )
                session.add(FormPricing(form_code=code, **prices))
                session.add(
                    FormPublication(
                        form_code=code,
                        city_slot=2,
                        city_id=city_id,
                        is_static=True,
                        is_visible=True,
                        is_verified=True,
                        has_medical_certificate=True,
                        sort_order=idx,
                    )
                )
                for order_idx, photo_url in enumerate(item.photos):
                    session.add(
                        FormPhoto(
                            form_code=code,
                            storage_key=photo_url[:512],
                            sort_order=order_idx,
                        )
                    )
                saved += 1

            await session.commit()
    finally:
        await db.close()
    return saved


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Parse static forms into escort_db")
    parser.add_argument("--city", default=None, help="Optional target city name in `cities` table")
    parser.add_argument("--url", default=DEFAULT_BASE_URL, help="Target site base URL")
    parser.add_argument("--limit", type=int, default=1000, help="Max forms to parse")
    parser.add_argument("--max-pages", type=int, default=200, help="Max listing pages to scan")
    parser.add_argument("--page-template", default=None, help="Optional URL template, e.g. '{base}/page/{page}/'")
    parser.add_argument("--proxy", default=None, help="Optional HTTP/SOCKS proxy URL")
    parser.add_argument("--html-dir", default=None, help="Optional directory with saved profile .html files")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, do not write to DB")
    args = parser.parse_args()

    if args.html_dir:
        forms = collect_from_dir(Path(args.html_dir), args.url, limit=args.limit)
    else:
        forms = await collect_from_web(
            args.url,
            limit=args.limit,
            max_pages=args.max_pages,
            proxy=args.proxy,
            page_template=args.page_template,
        )

    logger.info("Parsed %s forms for city=%s", len(forms), args.city)
    if args.dry_run or not forms:
        return

    db_url = os.getenv("DATABASE_URL") or "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    saved = await save_forms(db_url, args.city, forms)
    logger.info("Saved %s static forms into DB (city=%s)", saved, args.city)


if __name__ == "__main__":
    asyncio.run(async_main())
