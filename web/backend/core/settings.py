from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "escort_web"
    API_PORT: int = 8007

    WEB_DOMAIN: str = "localhost"
    BOT_USERNAME: str = "escort_main_bot"

    API_BASE_URL: str = "http://api:8000"
    LOGS_API_URL: str = "http://logs:8006"
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_api"

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
