from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "escort_logs"
    API_PORT: int = 8006

    # Внутренний секрет для валидации входящих событий от ботов
    LOGS_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_logs"

    # API service (для записи истории логов и подтверждения инвойсов)
    API_BASE_URL: str = "http://api:8000"
    API_SECRET_KEY: str = ""
    API_TARGET_AUDIENCE: str = "escort_api"

    # Telegram bot (aiogram) для отправки логов
    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "@escort_logs_bot"
    LOGS_CHAT_ID: int = 0

    # Webhook для бота логов (если нужен прием команд)
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""

    # Внутренний адрес admin-bot для личных логов воркерам
    ADMIN_BOT_URL: str = "http://admin-bot:8003"

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
