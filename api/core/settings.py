from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "escort_api"
    API_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://escort:escort@postgres:5432/escort"

    # Telegram Bot (для валидации Web App init_data клиента)
    BOT_TOKEN: str = ""
    WEB_APP_INIT_DATA_TTL_SECONDS: int = 86400

    # Photos service (публичный URL для отдачи фото в web_app)
    PHOTOS_API_URL: str = ""

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
