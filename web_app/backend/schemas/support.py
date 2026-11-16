from __future__ import annotations

from pydantic import BaseModel, Field


class SupportResponse(BaseModel):
    support_bot_url: str = Field("", alias="supportBotUrl")
    info_channel: str = Field("", alias="infoChannel")
    reviews_channel: str = Field("", alias="reviewsChannel")

    class Config:
        populate_by_name = True
        by_alias = True
