from core.settings import settings


def is_owner(user_id: int) -> bool:
    return bool(settings.OWNER_ID and int(user_id) == int(settings.OWNER_ID))
