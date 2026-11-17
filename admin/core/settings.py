from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = ""

    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""
    API_PORT: int = 8003

    DATABASE_URL: str = "postgresql+asyncpg://admin:P6jpA-TkrrKW@postgres:5432/escort_db"
    REDIS_URL: str = "redis://redis:6379/2"

    # API service
    API_BASE_URL: str = "http://api:8000"
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_api"
    ADMIN_API_KEY: str = ""

    LOGS_API_URL: str = "http://logs:8006"
    LOGS_SECRET_KEY: str = ""

    OWNER_ID: int = 0
    ADMIN_ALLOWED_IDS: str = ""
    ADMIN_RESULTS_PER_PAGE: int = 8

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

    @property
    def allowed_admin_ids(self) -> set[int]:
        result: set[int] = set()
        if self.OWNER_ID:
            result.add(int(self.OWNER_ID))
        for item in self.ADMIN_ALLOWED_IDS.split(","):
            item = item.strip()
            if item.isdigit():
                result.add(int(item))
        return result


settings = Settings()
