from fastapi import FastAPI

from api.routes import router as root_router
from core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    app.include_router(root_router)
    return app


__all__ = ["create_app"]
