from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path

from fastapi import UploadFile

from core.settings import settings
from services.watermark import apply_watermark, compress_avatar

ALLOWED_CATEGORIES = {"models", "clients"}
_ALLOWED_EXTENSIONS = {".jpg", ".png", ".webp", ".gif"}
_FILE_NAME_RE = re.compile(r"^[a-f0-9]{64}\.(jpg|png|webp|gif)$")


def ensure_storage_dir(category: str | None = None) -> Path:
    base = Path(settings.PHOTOS_STORAGE_PATH)
    if category:
        if category not in ALLOWED_CATEGORIES:
            raise ValueError("invalid_category")
        path = base / category
    else:
        path = base
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_valid_public_file_name(file_name: str) -> bool:
    return bool(_FILE_NAME_RE.fullmatch(file_name or ""))


def _write_atomic(target_path: Path, data: bytes) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        return
    file_descriptor, temp_path_raw = tempfile.mkstemp(
        prefix="upload_",
        suffix=target_path.suffix or ".tmp",
        dir=target_path.parent,
    )
    temp_path = Path(temp_path_raw)
    try:
        with os.fdopen(file_descriptor, "wb") as output:
            output.write(data)
        temp_path.replace(target_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


async def save_upload_stream(
    upload_file: UploadFile,
    *,
    extension: str,
    max_file_size_bytes: int,
    category: str = "models",
    chunk_size: int = 1024 * 1024,
) -> tuple[str, str]:
    if category not in ALLOWED_CATEGORIES:
        raise ValueError("invalid_category")
    if extension not in _ALLOWED_EXTENSIONS:
        raise ValueError("invalid_extension")

    storage_dir = ensure_storage_dir(category)
    raw_chunks: list[bytes] = []
    bytes_written = 0
    while True:
        chunk = await upload_file.read(chunk_size)
        if not chunk:
            break
        bytes_written += len(chunk)
        if bytes_written > max_file_size_bytes:
            raise ValueError("file_too_large")
        raw_chunks.append(chunk)

    data = b"".join(raw_chunks)
    if category == "clients" and extension != ".gif":
        try:
            data = compress_avatar(data)
            extension = ".jpg"
        except Exception:
            pass

    content_hash = hashlib.sha256(data).hexdigest()
    final_name = f"{content_hash}{extension}"
    _write_atomic(storage_dir / final_name, data)
    return final_name, content_hash


def get_file_path(file_name: str, *, category: str = "models") -> Path | None:
    if not is_valid_public_file_name(file_name) or category not in ALLOWED_CATEGORIES:
        return None
    path = ensure_storage_dir(category) / file_name
    if path.exists() and path.is_file():
        return path
    if category == "models":
        legacy_path = ensure_storage_dir() / file_name
        if legacy_path.exists() and legacy_path.is_file():
            return legacy_path
    return None


def get_model_serving_path(file_name: str) -> Path | None:
    """
    Return path to serve a model image: dynamically applies & caches the configured
    watermark on disk when PHOTOS_WATERMARK_ENABLED is true (for non-GIFs).
    """
    orig_path = get_file_path(file_name, category="models")
    if orig_path is None:
        return None
    if not settings.PHOTOS_WATERMARK_ENABLED or file_name.lower().endswith(".gif"):
        return orig_path

    wm_text = settings.PHOTOS_WATERMARK_TEXT.strip()
    if not wm_text:
        return orig_path

    wm_key = hashlib.sha256(f"{wm_text}:{settings.PHOTOS_WATERMARK_OPACITY}".encode()).hexdigest()[:12]
    cache_path = Path(settings.PHOTOS_STORAGE_PATH) / ".cache" / wm_key / f"{Path(file_name).stem}.jpg"
    if cache_path.exists() and cache_path.is_file():
        return cache_path

    try:
        watermarked = apply_watermark(
            orig_path.read_bytes(),
            text=wm_text,
            opacity=int(settings.PHOTOS_WATERMARK_OPACITY),
        )
        _write_atomic(cache_path, watermarked)
        return cache_path
    except Exception:
        return orig_path


def delete_file(file_name: str, *, category: str | None = None) -> bool:
    if not is_valid_public_file_name(file_name):
        return False
    if category is not None and category not in ALLOWED_CATEGORIES:
        return False

    deleted = False
    search_dirs: list[Path] = []
    if category is not None:
        search_dirs.append(ensure_storage_dir(category))
    else:
        for cat in ALLOWED_CATEGORIES:
            search_dirs.append(ensure_storage_dir(cat))
        search_dirs.append(ensure_storage_dir())

    for directory in search_dirs:
        candidate = directory / file_name
        if candidate.exists() and candidate.is_file():
            candidate.unlink()
            deleted = True

    cache_root = Path(settings.PHOTOS_STORAGE_PATH) / ".cache"
    if cache_root.exists():
        stem = Path(file_name).stem
        for cached in cache_root.glob(f"*/{stem}.*"):
            if cached.is_file():
                cached.unlink(missing_ok=True)
    return deleted
