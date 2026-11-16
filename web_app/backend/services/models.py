from __future__ import annotations

from backend.core.settings import settings
from backend.schemas.models import (
    FavoriteCodesResponse,
    ModelAdditionalItem,
    ModelDetailsResponse,
    ModelFlags,
    ModelListResponse,
    ModelPrices,
    ModelReviewItem,
    ModelServiceItem,
    ModelSummary,
)


def _resolve_photo_url(key: str, photos_base_url: str = "") -> str:
    cleaned = str(key or "").strip()
    if not cleaned:
        return ""
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    base = (photos_base_url or "").rstrip("/")
    if cleaned.startswith("/c/"):
        return f"{base}{cleaned}" if base else cleaned
    return f"{base}/c/{cleaned}" if base else f"/c/{cleaned}"


def build_model_summary(item, photos_base_url: str = "") -> ModelSummary:
    photos = [str(p).strip() for p in getattr(item, "photos", []) if str(p).strip()]
    photo_urls = [_resolve_photo_url(p, photos_base_url) for p in photos]
    preview_ref = photos[0] if photos else None
    preview_url = photo_urls[0] if photo_urls else None

    return ModelSummary(
        code=item.code,
        name=item.name,
        city_status=int(getattr(item, "city_status", 1) or 1),
        age=int(getattr(item, "age", 0) or 0),
        height=int(getattr(item, "height", 0) or 0),
        tits=int(getattr(item, "bust_size", 0) or 0),
        description=getattr(item, "caption", None),
        prices=ModelPrices(
            one_hour=getattr(item, "one_hour_price", None),
            two_hours=getattr(item, "two_hour_price", None),
            three_hours=getattr(item, "three_hour_price", None),
            night=getattr(item, "overnight_price", None),
        ),
        flags=ModelFlags(
            verification=bool(getattr(item, "is_verified", False)),
            document=bool(getattr(item, "has_medical_certificate", False)),
            dynamic=False,
        ),
        photo_refs=photos,
        photo_urls=photo_urls,
        preview_photo_ref=preview_ref,
        preview_photo_url=preview_url,
        orders=int(getattr(item, "orders", 0) or 0),
        rating=float(getattr(item, "rating", 0.0) or 0.0),
        reviews_count=int(getattr(item, "reviews_count", 0) or 0),
        is_favorite=bool(getattr(item, "is_favorite", False)),
    )


def build_model_list_response(forms) -> ModelListResponse:
    photos_url = settings.PHOTOS_API_URL
    return ModelListResponse(
        items=[
            build_model_summary(item, photos_url)
            for item in forms.items
        ]
    )


def build_model_details_response(card, *, reviews, services, additionals) -> ModelDetailsResponse:
    photos_url = settings.PHOTOS_API_URL
    summary = build_model_summary(card, photos_url)
    
    parsed_services = []
    for idx, s in enumerate(getattr(services, "items", [])):
        name = s.get("name", "") if isinstance(s, dict) else getattr(s, "name", str(s))
        if name:
            parsed_services.append(ModelServiceItem(id=idx + 1, name=str(name)))

    parsed_additionals = []
    for idx, a in enumerate(getattr(additionals, "items", [])):
        name = a.get("name", "") if isinstance(a, dict) else getattr(a, "name", str(a))
        price = int(a.get("price", 0) if isinstance(a, dict) else getattr(a, "price", 0))
        if name:
            parsed_additionals.append(ModelAdditionalItem(id=idx + 1, name=str(name), price=price))

    parsed_reviews = []
    for idx, r in enumerate(getattr(reviews, "items", [])):
        parsed_reviews.append(
            ModelReviewItem(
                id=idx + 1,
                author=getattr(r, "author", None),
                review_date=getattr(r, "review_date", None),
                body=getattr(r, "body", None),
                score=int(getattr(r, "score", 0) or 0),
            )
        )

    return ModelDetailsResponse(
        code=summary.code,
        name=summary.name,
        city_status=summary.city_status,
        age=summary.age,
        height=summary.height,
        tits=summary.tits,
        description=summary.description,
        prices=summary.prices,
        flags=summary.flags,
        photo_refs=summary.photo_refs,
        photo_urls=summary.photo_urls,
        preview_photo_ref=summary.preview_photo_ref,
        preview_photo_url=summary.preview_photo_url,
        orders=summary.orders,
        rating=summary.rating,
        reviews_count=len(parsed_reviews) or summary.reviews_count,
        is_favorite=summary.is_favorite,
        services=parsed_services,
        additionals=parsed_additionals,
        reviews=parsed_reviews,
    )


def build_favorite_codes_response(favorites) -> FavoriteCodesResponse:
    return FavoriteCodesResponse(
        codes=[
            item["form_code"] if isinstance(item, dict) else item.form_code
            for item in getattr(favorites, "items", [])
        ]
    )
