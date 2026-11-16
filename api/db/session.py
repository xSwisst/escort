from shared.db import create_db

from core.settings import settings

engine, async_session_maker, get_session = create_db(settings.DB_URL)
