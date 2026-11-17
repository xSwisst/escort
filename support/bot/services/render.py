from __future__ import annotations

from bot.assets.texts import t
from shared.utils.date import format_datetime_ru


def build_client_info_text(summary) -> str:
    full_name = " ".join(part for part in [summary.first_name, summary.last_name] if part).strip() or t("support_name_missing")
    return t(
        "support_info_card",
        full_name=full_name,
        username=f"@{summary.username}" if summary.username else t("support_username_missing"),
        user_id=summary.user_id,
        primary_city=summary.primary_city or t("support_city_missing"),
        secondary_city=summary.secondary_city or t("support_city_missing"),
        active_city_slot=summary.active_city_slot,
        promo=summary.promo or t("support_promo_missing"),
        title=summary.title or t("support_agreement_missing"),
        ban_status=t("support_ban_enabled") if summary.is_banned else t("support_ban_disabled"),
        forum_chat_id=summary.forum_chat_id or 0,
        topic_id=summary.topic_id or 0,
        registered_at=format_datetime_ru(summary.registered_at),
    )
