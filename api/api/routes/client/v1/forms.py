from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from clients.logs import emit_client_log
from services.clients.service import ClientService
from services.forms.service import FormService
from schemas.client import (
    FavoriteToggleResponse,
    FormAdditionalsResponse,
    FormCardResponse,
    FormListItem,
    FormPrivateChannelResponse,
    FormReviewsResponse,
    FormServicesResponse,
    FormsListResponse,
    ReviewItem,
)

router = APIRouter(prefix="/forms", tags=["client-forms"])


def _has_private_channel(form) -> bool:
    private_channel = getattr(form, "private_channel", None)
    return bool(private_channel and getattr(private_channel, "is_enabled", False) and getattr(private_channel, "subscription_price", None))


async def _get_form_or_404(form_service: FormService, form_code: str):
    form = await form_service.get_form(form_code)
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
    return form


def _serialize_photos(form) -> list[str]:
    return [str(photo.storage_key).strip() for photo in getattr(form, "photos", []) if str(photo.storage_key).strip()]


async def _build_form_card(session: AsyncSession, *, user_id: int, form_code: str) -> FormCardResponse:
    client_service = ClientService(session)
    form_service = FormService(session)
    form = await _get_form_or_404(form_service, form_code)
    reviews = await form_service.get_reviews(form_code)
    services = await form_service.get_services(form_code)
    additionals = await form_service.get_additionals(form_code)

    profile = form.profile
    pricing = form.pricing
    publication = form.publication

    return FormCardResponse(
        code=form.code,
        name=profile.name if profile else "",
        age=int(profile.age or 0) if profile else 0,
        height=int(profile.height or 0) if profile else 0,
        bust_size=int(profile.bust_size or 0) if profile else 0,
        one_hour_price=pricing.one_hour_price if pricing else None,
        two_hour_price=pricing.two_hour_price if pricing else None,
        three_hour_price=pricing.three_hour_price if pricing else None,
        overnight_price=pricing.overnight_price if pricing else None,
        caption=getattr(profile, "caption", getattr(profile, "description", None)) if profile else None,
        is_verified=bool(publication.is_verified) if publication else False,
        has_medical_certificate=bool(publication.has_medical_certificate) if publication else False,
        rating=form.rating,
        orders=int(form.orders_count or 0),
        public_channel_url=publication.public_channel_url if publication else None,
        photos=_serialize_photos(form),
        is_favorite=await form_service.is_favorite(user_id, form_code),
        has_reviews=bool(reviews),
        has_services=bool(services),
        has_additionals=bool(additionals),
        has_private_channel=_has_private_channel(form),
        discount_amount=await client_service.get_discount_amount(user_id),
    )


@router.get("", response_model=FormsListResponse)
async def list_forms(
    user_id: int = Query(...),
    active_city_slot: int | None = Query(default=None),
    session: AsyncSession = Depends(service_session),
) -> FormsListResponse:
    client_service = ClientService(session)
    client, _ = await client_service.get_or_create_client(user_id)
    form_service = FormService(session)
    forms = await form_service.get_visible_forms(client, active_city_slot=active_city_slot)
    favorites = {item.form_code for item in await form_service.favorites.get_by_user(user_id)}
    return FormsListResponse(
        items=[
            FormListItem(
                code=form.code,
                name=form.profile.name,
                age=int(form.profile.age or 0),
                height=int(form.profile.height or 0),
                bust_size=int(form.profile.bust_size or 0),
                one_hour_price=form.pricing.one_hour_price,
                two_hour_price=form.pricing.two_hour_price,
                three_hour_price=form.pricing.three_hour_price,
                overnight_price=form.pricing.overnight_price,
                caption=getattr(form.profile, "caption", getattr(form.profile, "description", None)),
                is_verified=bool(form.publication.is_verified),
                has_medical_certificate=bool(form.publication.has_medical_certificate),
                rating=form.rating,
                orders=int(form.orders_count or 0),
                photos=_serialize_photos(form),
                is_favorite=form.code in favorites,
            )
            for form in forms
        ]
    )


@router.get("/{form_code}/card", response_model=FormCardResponse)
async def get_form_card(
    form_code: str,
    user_id: int = Query(...),
    session: AsyncSession = Depends(service_session),
) -> FormCardResponse:
    client_service = ClientService(session)
    form_service = FormService(session)
    form = await _get_form_or_404(form_service, form_code)
    client, _ = await client_service.get_or_create_client(user_id)

    try:
        await emit_client_log(
            "open_model_form",
            client,
            actor_id=user_id,
            form_id=form.id,
            code=form.code,
            model_name=form.profile.name if form.profile else form.code,
        )
    except Exception:
        pass

    return await _build_form_card(session, user_id=user_id, form_code=form_code)


@router.post("/{form_code}/favorite", response_model=FavoriteToggleResponse)
async def toggle_favorite(
    form_code: str,
    user_id: int = Query(...),
    session: AsyncSession = Depends(service_session),
) -> FavoriteToggleResponse:
    form_service = FormService(session)
    await _get_form_or_404(form_service, form_code)
    is_favorite = await form_service.toggle_favorite(user_id, form_code)
    return FavoriteToggleResponse(is_favorite=is_favorite)


@router.get("/{form_code}/reviews", response_model=FormReviewsResponse)
async def get_reviews(
    form_code: str,
    session: AsyncSession = Depends(service_session),
) -> FormReviewsResponse:
    form_service = FormService(session)
    form = await _get_form_or_404(form_service, form_code)
    reviews = await form_service.get_reviews(form_code)
    return FormReviewsResponse(
        form_code=form_code,
        form_name=form.profile.name,
        items=[
            ReviewItem(
                author=review.author,
                review_date=review.review_date,
                body=review.body,
                score=int(review.score or 0),
            )
            for review in reviews
        ],
    )


@router.get("/{form_code}/additionals", response_model=FormAdditionalsResponse)
async def get_additionals(
    form_code: str,
    session: AsyncSession = Depends(service_session),
) -> FormAdditionalsResponse:
    form_service = FormService(session)
    await _get_form_or_404(form_service, form_code)
    rows = await form_service.get_additionals(form_code)
    return FormAdditionalsResponse(
        form_code=form_code,
        items=[{"name": str(row.name), "price": int(row.price)} for row in rows],
    )


@router.get("/{form_code}/services", response_model=FormServicesResponse)
async def get_services(
    form_code: str,
    session: AsyncSession = Depends(service_session),
) -> FormServicesResponse:
    form_service = FormService(session)
    await _get_form_or_404(form_service, form_code)
    rows = await form_service.get_services(form_code)
    return FormServicesResponse(
        form_code=form_code,
        items=[{"name": str(row.name)} for row in rows if row.name],
    )


@router.get("/{form_code}/private-channel", response_model=FormPrivateChannelResponse)
async def get_private_channel(
    form_code: str,
    session: AsyncSession = Depends(service_session),
) -> FormPrivateChannelResponse:
    form_service = FormService(session)
    form = await _get_form_or_404(form_service, form_code)
    if not _has_private_channel(form):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Private channel not found")
    private_channel = form.private_channel
    return FormPrivateChannelResponse(
        form_code=form.code,
        name=form.profile.name,
        price=int(getattr(private_channel, "subscription_price", 0) or 0),
        description=str(getattr(private_channel, "description", "") or "").strip() or None,
    )
