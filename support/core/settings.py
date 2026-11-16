from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = ""

    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""
    API_PORT: int = 8002

    DATABASE_URL: str = "postgresql+asyncpg://escort:escort@postgres:5432/escort"
    REDIS_URL: str = "redis://redis:6379/1"

    LOGS_API_URL: str = "http://logs:8006"
    LOGS_SECRET_KEY: str = ""
    SUPPORT_FORUM_CHAT_ID: int = 0

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
