from __future__ import annotations

import ast

from bot.assets.media import get_banner_file


def clean_media_ref(photo_ref: str) -> str:
    raw = str(photo_ref or "").strip()
    while len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'", "`"}:
        raw = raw[1:-1].strip()
    return raw.strip("`").strip()


def safe_parse_photos(raw: str | None) -> list[str]:
    try:
        photos = ast.literal_eval(raw) if raw else []
    except Exception:
        photos = []
    if not isinstance(photos, list):
        return []
    return [ref for item in photos if (ref := clean_media_ref(str(item)))]


def media_refs(photos: list[str] | None) -> list[str]:
    return [ref for item in photos or [] if (ref := clean_media_ref(str(item)))]


def pick_first_media_ref(photos: list[str] | None, fallback_ref: str) -> str:
    refs = media_refs(photos)
    return refs[0] if refs else fallback_ref


def models_banner_media() -> str:
    return get_banner_file("models-banner")
