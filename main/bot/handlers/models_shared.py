from bot.keyboards.models_catalog import kb_model_card
from clients.api import ApiNotFoundError, api_client
from utils.form_text import build_form_text
from utils.helpers import media_refs


def has_private_channel(form) -> bool:
    return bool(getattr(form, "has_private_channel", False))


def build_form_card(form, *, cta: bool = False, discount_amount: int | None = None) -> str:
    return build_form_text(form, cta=cta, discount_amount=discount_amount if discount_amount is not None else getattr(form, "discount_amount", None))


def build_form_card_markup(form, code: str, *, back_target: str = "menu:models"):
    actual_code = getattr(form, "code", None) or code
    return kb_model_card(
        actual_code,
        form.is_favorite,
        has_reviews=form.has_reviews,
        has_services=form.has_services,
        has_additionals=form.has_additionals,
        blog_url=getattr(form, "public_channel_url", None),
        has_private_channel=has_private_channel(form),
        order_available=True,
        back_target=back_target,
    )



async def get_form_card_payload(
    user_id: int,
    code: str,
    *,
    photo_idx: int = 0,
    fallback_media: str | None = None,
    back_target: str = "menu:models",
):
    try:
        form = await api_client.forms.get_form_card(user_id=user_id, form_code=code)
    except ApiNotFoundError:
        return None

    refs = media_refs(form.photos)
    if fallback_media:
        media_ref = refs[photo_idx % len(refs)] if refs else fallback_media
    elif refs:
        media_ref = refs[photo_idx % len(refs)]
    else:
        media_ref = None

    actual_code = getattr(form, "code", None) or code
    return media_ref, build_form_card(form, cta=False), build_form_card_markup(form, actual_code, back_target=back_target)
