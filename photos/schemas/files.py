from __future__ import annotations

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_name: str
    content_hash: str
    content_type: str
    path: str
    public_url: str | None = None


class FileDeleteResponse(BaseModel):
    ok: bool = True
    file_name: str


class HealthResponse(BaseModel):
    ok: bool = True
    service: str
