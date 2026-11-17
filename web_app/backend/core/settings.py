from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "escort_web_app_backend"
    API_PORT: int = 8004

    # Internal API
    API_BASE_URL: str = "http://api:8000"
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "escort_api"

    # Internal Logs
    LOGS_API_URL: str = "http://logs:8006"
    LOGS_SECRET_KEY: str = ""

    # Photos
    PHOTOS_API_URL: str = ""

    # User Sessions
    WEB_APP_SESSION_SECRET: str = ""
    WEB_APP_SESSION_AUDIENCE: str = "escort_web_app_user"
    WEB_APP_SESSION_TTL_HOURS: int = 24
    WEB_APP_BOT_TOKEN: str = ""
    WEB_APP_ENABLE_MOCK_SESSION: bool = False

    # Links
    WEB_APP_INFO_CHANNEL_URL: str = ""
    WEB_APP_REVIEWS_CHANNEL_URL: str = ""
    WEB_APP_SUPPORT_BOT_URL: str = ""
    WEB_APP_TITLE: str = "Escort Mini App"

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
