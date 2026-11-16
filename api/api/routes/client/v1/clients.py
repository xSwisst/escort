from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import db_session, service_session
from clients.logs import emit_client_log
from core.settings import settings
from core.web_app_auth import validate_telegram_init_data
from domain.clients.service import ClientService
from repositories.client_logs import ClientActivityLogRepository
from schemas.client import (
    AcceptAgreementRequest,
    ActionStatusResponse,
    AgreementInfo,
    ClientCitiesResponse,
    ClientIdentity,
    SetCityRequest,
    StartBootstrapRequest,
    StartBootstrapResponse,
    SwitchCityRequest,
    TelegramUserPayload,
)

router = APIRouter(prefix="/clients", tags=["client-clients"])


def _active_city(client) -> str | None:
    active_city_slot = int(getattr(client, "active_city_slot", 1) or 1)
    if active_city_slot == 2 and getattr(client, "secondary_city", None):
        return client.secondary_city
    return getattr(client, "primary_city", None) or getattr(client, "secondary_city", None)


async def _cities_or_404(service: ClientService, user_id: int) -> tuple[object, ClientCitiesResponse]:
    client = await service.get_client(user_id)
    if not client:
        client, created = await service.get_or_create_client(user_id)
        if created:
            await service._session.commit()
            await emit_client_log("new_user", client)
    return client, ClientCitiesResponse(
        primary_city=client.primary_city,
        secondary_city=client.secondary_city,
        active_city_slot=int(client.active_city_slot or 1),
        active_city=_active_city(client),
    )


@router.post("/bootstrap", response_model=StartBootstrapResponse)
async def bootstrap_client(
    payload: StartBootstrapRequest,
    session: AsyncSession = Depends(db_session),
) -> StartBootstrapResponse:
    service = ClientService(session)

    # Validate init_data if provided, otherwise use user payload directly
    if payload.init_data:
        try:
            user_data = validate_telegram_init_data(
                payload.init_data,
                bot_token=settings.BOT_TOKEN,
                max_age_seconds=int(settings.WEB_APP_INIT_DATA_TTL_SECONDS or 3600),
            )
            user_id = user_data["id"]
            first_name = user_data.get("first_name")
            last_name = user_data.get("last_name")
            username = user_data.get("username")
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    elif payload.user:
        user_id = payload.user.user_id
        first_name = payload.user.first_name
        last_name = payload.user.last_name
        username = payload.user.username
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either init_data or user is required")

    client, created = await service.get_or_create_client(
        user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
    )
    agreement = await service.get_active_agreement(user_id)
    activity_repo = ClientActivityLogRepository(session)
    has_registered_log = await activity_repo.has_user_event(user_id, "new_user")

    if created or not has_registered_log:
        await session.commit()
        await emit_client_log("new_user", client)
    return StartBootstrapResponse(
        client=ClientIdentity(user_id=client.user_id, has_accepted_agreement=bool(client.has_accepted_agreement)),
        agreement_required=not bool(client.has_accepted_agreement) and agreement is not None,
        agreement=AgreementInfo(
            agreement_id=getattr(agreement, "agreement_id", None),
            title=getattr(agreement, "title", None),
            document_url=getattr(agreement, "document_url", None),
        ) if agreement else None,
        user=TelegramUserPayload(
            user_id=client.user_id,
            first_name=client.first_name,
            last_name=client.last_name,
            username=client.username,
        ),
    )


@router.post("/accept-agreement", response_model=ActionStatusResponse)
async def accept_agreement(
    payload: AcceptAgreementRequest,
    session: AsyncSession = Depends(db_session),
) -> ActionStatusResponse:
    service = ClientService(session)
    client = await service.get_client(payload.user_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    agreement = await service.get_active_agreement(payload.user_id)
    if agreement:
        await service.set_agreement(payload.user_id, agreement.agreement_id)
        await emit_client_log("agreement_accepted", client, agreement_id=agreement.agreement_id)
        return ActionStatusResponse()

    await service.clients.update_by_user_id(payload.user_id, has_accepted_agreement=True)
    await emit_client_log("agreement_accepted", client, agreement_id=None)
    return ActionStatusResponse()


@router.get("/{user_id}/cities", response_model=ClientCitiesResponse)
async def get_user_cities(
    user_id: int,
    session: AsyncSession = Depends(db_session),
) -> ClientCitiesResponse:
    _, cities = await _cities_or_404(ClientService(session), user_id)
    return cities


@router.post("/{user_id}/cities", response_model=ClientCitiesResponse)
async def set_user_city(
    user_id: int,
    payload: SetCityRequest,
    session: AsyncSession = Depends(db_session),
) -> ClientCitiesResponse:
    service = ClientService(session)

    # Получаем старый город перед изменением
    client = await service.get_client(user_id)
    old_city = client.primary_city if payload.slot == 1 else client.secondary_city

    await service.set_city(user_id, payload.city, payload.slot)
    await service.clients.update_by_user_id(user_id, active_city_slot=payload.slot)
    client, cities = await _cities_or_404(service, user_id)

    # Определяем тип события
    event_type = "add_city" if not old_city else "change_of_city"
    extra = {"city": payload.city}
    if old_city:
        extra["old_city"] = old_city
        extra["new_city"] = payload.city

    await emit_client_log(event_type, client, **extra)
    return cities


@router.post("/{user_id}/cities/switch", response_model=ClientCitiesResponse)
async def switch_user_city(
    user_id: int,
    payload: SwitchCityRequest,
    session: AsyncSession = Depends(db_session),
) -> ClientCitiesResponse:
    service = ClientService(session)
    client, cities = await _cities_or_404(service, user_id)

    old_city = client.primary_city if client.active_city_slot == 1 else client.secondary_city
    target_city = client.primary_city if payload.active_city_slot == 1 else client.secondary_city

    if not target_city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City slot not set")

    await service.clients.update_by_user_id(user_id, active_city_slot=payload.active_city_slot)
    _, cities = await _cities_or_404(service, user_id)

    await emit_client_log(
        "change_of_city",
        client,
        old_city=old_city,
        new_city=target_city,
    )
    return cities
