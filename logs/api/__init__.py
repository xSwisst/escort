from __future__ import annotations

from fastapi import FastAPI

from api.routes import router as v1_router
from core.settings import settings


def create_api_app() -> FastAPI:
    """Create the FastAPI application for the logs service HTTP API."""
    app = FastAPI(title=settings.APP_NAME)
    app.include_router(v1_router)
    return app


create_app = create_api_app

__all__ = ["create_api_app", "create_app"]
