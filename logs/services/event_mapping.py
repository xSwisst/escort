"""
Маппинг событий на типы тредов для отправки логов.
"""

from __future__ import annotations


# Типы тредов
class LogThreadType:
    CLIENT_REGISTRATION = "client_registration"
    CLIENT_AGREEMENT = "client_agreement"
    CLIENT_CITIES = "client_cities"
    CLIENT_ADDRESSES = "client_addresses"
    PAYMENT_CHECKS = "payment_checks"
    PAYMENT_REQUESTS = "payment_requests"
    CLIENT_SUPPORT_SECTION = "client_support_section"
    CLIENT_SUPPORT_MESSAGES = "client_support_messages"
    PROMOCODE_ACTIVATED = "promocode_activated"
    ORDERS = "orders"
    FORMS_VIEWS = "forms_views"
    MAILING = "mailing"
    REVIEWS = "reviews"
    FORMS_MANAGEMENT = "forms_management"
    PROMOCODE_CREATED = "promocode_created"


# Маппинг имени события на тип треда
EVENT_TO_THREAD_MAP: dict[str, str] = {
    # Регистрации
    "new_user": LogThreadType.CLIENT_REGISTRATION,

    # Соглашения
    "agreement_accepted": LogThreadType.CLIENT_AGREEMENT,

    # Города
    "add_city": LogThreadType.CLIENT_CITIES,
    "change_of_city": LogThreadType.CLIENT_CITIES,

    # Адреса
    "add_address": LogThreadType.CLIENT_ADDRESSES,
    "remove_address": LogThreadType.CLIENT_ADDRESSES,

    # Чеки
    "get_check_of_top_up": LogThreadType.PAYMENT_CHECKS,
    "get_check_of_payment_private_channel": LogThreadType.PAYMENT_CHECKS,
    "get_check_of_payment_model": LogThreadType.PAYMENT_CHECKS,

    # Заявки на пополнения
    "payment_request": LogThreadType.PAYMENT_REQUESTS,

    # Раздел поддержки
    "open_support_section": LogThreadType.CLIENT_SUPPORT_SECTION,

    # Сообщения в поддержку
    "message_to_support": LogThreadType.CLIENT_SUPPORT_MESSAGES,

    # Создание промокода
    "promocode_created": LogThreadType.PROMOCODE_CREATED,

    # Активация промокода
    "promocode_activated": LogThreadType.PROMOCODE_ACTIVATED,

    # Оформления
    "new_order": LogThreadType.ORDERS,

    # Открытие анкеты
    "open_model_form": LogThreadType.FORMS_VIEWS,

    # Анкеты (создание)
    "new_form": LogThreadType.FORMS_MANAGEMENT,

    # Отзывы
    "new_review": LogThreadType.REVIEWS,

    # Рассылка
    "mailing": LogThreadType.MAILING,
}


def get_thread_type_for_event(event_name: str) -> str:
    """
    Возвращает тип треда для события.
    Если событие не найдено в маппинге, возвращает дефолтный тред для сообщений поддержки.
    """
    return EVENT_TO_THREAD_MAP.get(event_name, LogThreadType.CLIENT_SUPPORT_MESSAGES)
