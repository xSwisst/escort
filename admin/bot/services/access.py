from core.settings import settings


def is_admin_allowed(user_id: int) -> bool:
    return int(user_id) in settings.allowed_admin_ids
