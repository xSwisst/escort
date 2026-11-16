import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles


from backend.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "web"}

    @app.get("/api/config")
    async def get_config():
        return {
            "app_name": settings.APP_NAME,
            "bot_username": settings.BOT_USERNAME,
            "web_domain": settings.WEB_DOMAIN,
        }

    # Frontend dist path
    dist_path = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist_path.exists():
        if (dist_path / "assets").exists():
            app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            file_path = dist_path / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)

            index_file = dist_path / "index.html"
            if index_file.exists():
                html = index_file.read_text(encoding="utf-8")
                bot_user = settings.BOT_USERNAME.lstrip("@")
                config_json = json.dumps({"bot_username": bot_user, "web_domain": settings.WEB_DOMAIN})
                script_tag = f"<script>window.__APP_CONFIG__={config_json};</script>"
                if "</head>" in html:
                    html = html.replace("</head>", f"{script_tag}</head>", 1)
                elif "</body>" in html:
                    html = html.replace("</body>", f"{script_tag}</body>", 1)
                return HTMLResponse(content=html, media_type="text/html")
            return HTMLResponse(content="<h1>Index file not found</h1>", status_code=404)

    else:
        @app.get("/")
        async def root():
            return {"status": "Web landing backend is running"}

    return app


__all__ = ["create_app"]
