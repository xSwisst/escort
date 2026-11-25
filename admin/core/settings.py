from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = ""

    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""
    API_PORT: int = 8003

    DATABASE_URL: str = "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    REDIS_URL: str = "redis://redis:6379/2"

    # API & internal services
    API_BASE_URL: str = "http://api:8000"
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_api"
    ADMIN_API_KEY: str = ""
    MAIN_BOT_URL: str = "http://main-bot:8001"

    LOGS_API_URL: str = "http://logs:8006"
    LOGS_SECRET_KEY: str = ""

    OWNER_ID: int = 0

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
