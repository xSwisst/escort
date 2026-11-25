from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "escort_photos"
    API_PORT: int = 8005

    # Service-to-service JWT
    API_SECRET_KEY: str = ""
    API_AUDIENCE: str = "photos_service"
    ALLOWED_ISSUERS: str = "api,escort_api,admin,main,support,logs"

    PHOTOS_STORAGE_PATH: str = "/data/photos"
    PHOTOS_SCHEME: str = "https"
    PHOTOS_DOMAIN: str = ""
    PHOTOS_MAX_FILE_SIZE_MB: int = 15
    PHOTOS_WATERMARK_ENABLED: bool = True
    PHOTOS_WATERMARK_TEXT: str = "elegant-agency.fun"
    PHOTOS_WATERMARK_OPACITY: int = 115

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

    @property
    def allowed_issuers(self) -> set[str]:
        return {item.strip() for item in self.ALLOWED_ISSUERS.split(",") if item.strip()}

    @property
    def max_file_size_bytes(self) -> int:
        return max(1, self.PHOTOS_MAX_FILE_SIZE_MB) * 1024 * 1024

    @property
    def public_base_url(self) -> str:
        domain = str(self.PHOTOS_DOMAIN or "").strip().strip("`").strip()
        if not domain:
            return ""
        if domain.startswith(("http://", "https://")):
            return domain.rstrip("/")
        scheme = str(self.PHOTOS_SCHEME or "https").strip().lower() or "https"
        return f"{scheme}://{domain.lstrip('/')}".rstrip("/")


settings = Settings()
