from __future__ import annotations

from pydantic import BaseModel, Field


class AboutResponse(BaseModel):
    title: str = "Escort Agency"
    agreement_url: str | None = Field(None, alias="agreementUrl")
    api_url: str | None = Field(None, alias="apiUrl")
    web_app_url: str | None = Field(None, alias="webAppUrl")
    info_channel: str = Field("", alias="infoChannel")
    reviews_channel: str = Field("", alias="reviewsChannel")
    sections: list[str] = Field(default_factory=lambda: ["about", "models", "support", "profile"])

    class Config:
        populate_by_name = True
        by_alias = True
