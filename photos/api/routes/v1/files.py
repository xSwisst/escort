from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from api.dependencies import service_auth
from assets.texts import t
from core.settings import settings
from schemas import FileDeleteResponse, FileUploadResponse
from services import delete_file, get_file_path, save_upload_stream

router = APIRouter(tags=["photos-files"])

_ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _build_public_url(file_name: str) -> str | None:
    if not settings.public_base_url:
        return None
    return f"{settings.public_base_url}/c/{file_name}"


def _media_type(file_name: str) -> str:
    extension = Path(file_name).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(extension, "application/octet-stream")


@router.post("/internal/v1/files", response_model=FileUploadResponse)
async def upload_file(
    _: dict = Depends(service_auth),
    file: UploadFile = File(...),
) -> FileUploadResponse:
    if file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error_file_is_required"))
    extension = _ALLOWED_TYPES.get(file.content_type or "")
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("error_unsupported_file_type", content_type=file.content_type or "unknown"),
        )

    try:
        file_name, content_hash = await save_upload_stream(
            file,
            extension=extension,
            max_file_size_bytes=settings.max_file_size_bytes,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "file_too_large":
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=t("error_file_too_large")) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error_invalid_file_name")) from exc
    finally:
        await file.close()

    return FileUploadResponse(
        file_name=file_name,
        content_hash=content_hash,
        content_type=file.content_type or "application/octet-stream",
        path=f"/c/{file_name}",
        public_url=_build_public_url(file_name),
    )


@router.delete("/internal/v1/files/{file_name}", response_model=FileDeleteResponse)
async def remove_file(
    file_name: str,
    _: dict = Depends(service_auth),
) -> FileDeleteResponse:
    if not delete_file(file_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error_file_not_found"))
    return FileDeleteResponse(file_name=file_name)


@router.get("/c/{file_name}")
async def get_public_file(file_name: str):
    path = get_file_path(file_name)
    if path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error_file_not_found"))
    return FileResponse(path, media_type=_media_type(file_name))
