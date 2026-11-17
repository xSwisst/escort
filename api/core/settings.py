from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "escort_api"
    API_PORT: int = 8000

    # Service-to-service JWT
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_api"

    # Database (поддержка и DATABASE_URL и DB_URL)
    DATABASE_URL: str = "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    DB_URL: str = "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"

    # Telegram Bot (для валидации Web App init_data клиента)
    BOT_TOKEN: str = ""
    WEB_APP_INIT_DATA_TTL_SECONDS: int = 86400

    # Photos service (публичный URL для отдачи фото в web_app)
    PHOTOS_API_URL: str = ""
    LOGS_API_URL: str = "http://logs:8006"
    LOGS_SECRET_KEY: str = ""

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
