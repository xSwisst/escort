from __future__ import annotations

BANNERS: dict[str, str] = {
    # Основные разделы
    "agreement-banner": "agreement.jpg",
    "main-menu-banner": "menu.jpg",
    "info-banner": "information.png",
    "support-banner": "support.jpg",
    "models-banner": "models.jpg",
    "profile-banner": "profile.png",
    "choice-city-banner": "city.png",
    "city-banner": "city.png",

    # Профиль, заказы, пополнение и промокод
    "orders-banner": "order.png",
    "order-banner": "order.png",
    "top-up-banner": "top_up.png",
    "promo-banner": "promo.png",
    "enter-promo-banner": "promo.png",
    "promo-found-banner": "promo.png",
    "promo-not-found-banner": "promo.png",
    "promo-activate-banner": "promo.png",

    # Адреса
    "address-banner": "address.png",

    # Поиск по коду анкеты
    "enter-model-code-banner": "enter_code.png",
    "code-not-found-banner": "enter_code.png",

    # Оформление заказа модели (шаги заказа)
    "choice-tariff-plan-banner": "tariff_plan.png",
    "tariff-banner": "tariff_plan.png",
    "date-meeting-banner": "date_meeting.png",
    "place-meeting-banner": "place_meeting.png",
    "additional-banner": "additionals.png",

    # Оплата
    "payment-method-banner": "payment.png",
    "payment-banner": "payment.png",
    "payment-success-banner": "payment.png",
    "payment-unavailable-banner": "payment.png",
    "send-check-banner": "payment.png",
    "check-sent-banner": "payment.png",
}


def get_banner_file(banner_key: str) -> str:
    return BANNERS.get(banner_key, banner_key)
