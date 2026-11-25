from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path

from fastapi import UploadFile

from core.settings import settings
from services.watermark import WATERMARK_TEXT, apply_watermark

_ALLOWED_EXTENSIONS = {".jpg", ".png", ".webp", ".gif"}
_FILE_NAME_RE = re.compile(r"^[a-f0-9]{64}\.(jpg|png|webp|gif)$")


def ensure_storage_dir() -> Path:
    path = Path(settings.PHOTOS_STORAGE_PATH)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_valid_public_file_name(file_name: str) -> bool:
    return bool(_FILE_NAME_RE.fullmatch(file_name or ""))


async def save_upload_stream(
    upload_file: UploadFile,
    *,
    extension: str,
    max_file_size_bytes: int,
    chunk_size: int = 1024 * 1024,
) -> tuple[str, str]:
    storage_dir = ensure_storage_dir()
    if extension not in _ALLOWED_EXTENSIONS:
        raise ValueError("invalid_extension")

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
    if extension != ".gif":
        try:
            data = apply_watermark(data, text=WATERMARK_TEXT)
            extension = ".jpg"
        except Exception:
            pass

    content_hash = hashlib.sha256(data).hexdigest()
    final_name = f"{content_hash}{extension}"
    final_path = storage_dir / final_name
    if not final_path.exists():
        file_descriptor, temp_path_raw = tempfile.mkstemp(prefix="upload_", suffix=extension, dir=storage_dir)
        temp_path = Path(temp_path_raw)
        try:
            with os.fdopen(file_descriptor, "wb") as output:
                output.write(data)
            temp_path.replace(final_path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
    return final_name, content_hash


def get_file_path(file_name: str) -> Path | None:
    if not is_valid_public_file_name(file_name):
        return None
    path = ensure_storage_dir() / file_name
    if path.exists() and path.is_file():
        return path
    return None


def delete_file(file_name: str) -> bool:
    path = get_file_path(file_name)
    if path is None:
        return False
    path.unlink()
    return True
