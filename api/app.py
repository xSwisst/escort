from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from api.routes.client.v1 import router as client_v1_router
from api.routes.health import router as health_router
from core.settings import settings
from repository.models import Base
from repository.session import Database

db = Database(settings.DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(
                text(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_name = 'client_activity_logs'
                        ) THEN
                            ALTER TABLE client_activity_logs DROP CONSTRAINT IF EXISTS client_activity_logs_user_id_fkey;
                            ALTER TABLE client_activity_logs ALTER COLUMN client_id TYPE BIGINT;
                            ALTER TABLE client_activity_logs DROP COLUMN IF EXISTS icon_url;
                        END IF;
                    END $$;
                    """
                )
            )
        except Exception:
            pass
    yield
    await db.close()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(client_v1_router)
    return app


app = create_app()
