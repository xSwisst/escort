from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = ""

    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""
    API_PORT: int = 8002

    DATABASE_URL: str = "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    REDIS_URL: str = "redis://redis:6379/1"

    # API service
    API_BASE_URL: str = "http://api:8000"
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_api"

    LOGS_API_URL: str = "http://logs:8006"
    LOGS_SECRET_KEY: str = ""
    SUPPORT_FORUM_CHAT_ID: int = 0

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
