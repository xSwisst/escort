from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram.types import Message

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(slots=True, frozen=True)
class CachedMedia:
    filename: str
    file_id: str
    kind: str


_MEDIA_CACHE: dict[str, CachedMedia] = {}


def _service_root() -> tuple[Path, str]:
    settings_module = import_module("core.settings")
    settings = settings_module.settings
    service_root = Path(settings_module.__file__).resolve().parent.parent
    media_path = getattr(settings, "MEDIA_PATH", "assets/media")
    return service_root, str(media_path)


def _resolve_requested_file(filename: str) -> Path | None:
    service_root, media_path = _service_root()
    media_dir = (service_root / media_path).resolve()
    requested = (filename or "").strip()
    if not requested:
        return None

    direct = media_dir / requested
    if direct.exists() and direct.is_file():
        return direct

    stem = Path(requested).stem
    for ext in PHOTO_EXTENSIONS:
        candidate = media_dir / f"{stem}{ext}"
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _detect_media_kind(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in PHOTO_EXTENSIONS:
        return "photo"
    return None


async def get_cached(filename: str, **_: object) -> str | None:
    entry = _MEDIA_CACHE.get((filename or "").strip())
    return entry.file_id if entry else None


def get_cached_kind(filename: str) -> str | None:
    entry = _MEDIA_CACHE.get((filename or "").strip())
    if entry:
        return entry.kind
    path = _resolve_requested_file(filename)
    return _detect_media_kind(path) if path else None


def get_media_path(filename: str) -> Path | None:
    return _resolve_requested_file(filename)


def cache_media(filename: str, file_id: str, kind: str) -> None:
    if kind != "photo":
        return
    resolved = _resolve_requested_file(filename)
    actual_name = resolved.name if resolved is not None else Path(filename).name
    entry = CachedMedia(filename=actual_name, file_id=file_id, kind="photo")
    for alias in {actual_name, Path(filename).stem}:
        if alias:
            _MEDIA_CACHE[alias] = entry


def cache_message_media(filename: str, message: "Message | bool | None") -> None:
    if not message:
        return
    if hasattr(message, "photo") and message.photo:
        cache_media(filename, message.photo[-1].file_id, "photo")
