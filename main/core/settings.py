from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_PORT: int = 8001

    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "@escort_main_bot"

    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""

    DATABASE_URL: str = "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    REDIS_URL: str = "redis://redis:6379/0"

    # API service (for legacy handlers compatibility)
    API_BASE_URL: str = "http://api:8000"
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_api"

    # Internal logs service
    LOGS_API_URL: str = "http://logs:8006"
    LOGS_SECRET_KEY: str = ""

    SUPPORT_BOT_URL: str = "https://t.me/escort_support_bot"
    WEB_APP_URL: str = ""

    OWNER_ID: int = 0

    # Media path
    MEDIA_PATH: str = "bot/assets/media"

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
