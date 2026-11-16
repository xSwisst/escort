from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes.v1 import router as v1_router
from backend.clients.api import api_client
from backend.core.settings import settings


async def _close_clients() -> None:
    await api_client.close()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    
    # API routes first
    app.include_router(v1_router)

    # Frontend static files - only if dist exists
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    else:
        # Simple root handler if no frontend built
        @app.get("/")
        async def root():
            return {"status": "Web app backend is running", "api_prefix": "/web-app/api/v1"}

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await _close_clients()

    return app


__all__ = ["create_app"]
