from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from clients.logs import emit_client_log
from domain.addresses.service import AddressService
from schemas.client import (
    ActionStatusResponse,
    AddressCreateRequest,
    AddressItem,
    AddressListResponse,
    AddressUpdateAddressRequest,
    AddressUpdateTitleRequest,
)

router = APIRouter(prefix="/addresses", tags=["client-addresses"])


def _serialize_address(address) -> AddressItem:
    return AddressItem(id=address.id, title=address.label, address=address.full_address)


async def _get_owned_address_or_404(service: AddressService, user_id: int, address_id: int):
    address = await service.get_address(address_id)
    if not address or address.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


@router.get("/{user_id}", response_model=AddressListResponse)
async def list_addresses(
    user_id: int,
    session: AsyncSession = Depends(service_session),
) -> AddressListResponse:
    items = await AddressService(session).list_user_addresses(user_id)
    return AddressListResponse(items=[_serialize_address(item) for item in items])


@router.get("/{user_id}/{address_id}", response_model=AddressItem)
async def get_address(
    user_id: int,
    address_id: int,
    session: AsyncSession = Depends(service_session),
) -> AddressItem:
    return _serialize_address(await _get_owned_address_or_404(AddressService(session), user_id, address_id))


@router.post("/{user_id}", response_model=AddressItem)
async def create_address(
    user_id: int,
    payload: AddressCreateRequest,
    session: AsyncSession = Depends(service_session),
) -> AddressItem:
    service = AddressService(session)
    address = await service.create_address(user_id, title=payload.title, address=payload.address)

    client = await service.clients.get_by_user_id(user_id)
    await emit_client_log(
        "add_address",
        client,
        actor_id=user_id,
        address_name=address.label,
        address=address.full_address,
    )
    return _serialize_address(address)


@router.patch("/{user_id}/{address_id}/title", response_model=AddressItem)
async def update_address_title(
    user_id: int,
    address_id: int,
    payload: AddressUpdateTitleRequest,
    session: AsyncSession = Depends(service_session),
) -> AddressItem:
    service = AddressService(session)
    await _get_owned_address_or_404(service, user_id, address_id)
    address = await service.update_address(address_id, label=payload.title)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return _serialize_address(address)


@router.patch("/{user_id}/{address_id}/address", response_model=AddressItem)
async def update_address_body(
    user_id: int,
    address_id: int,
    payload: AddressUpdateAddressRequest,
    session: AsyncSession = Depends(service_session),
) -> AddressItem:
    service = AddressService(session)
    await _get_owned_address_or_404(service, user_id, address_id)
    address = await service.update_address(address_id, full_address=payload.address)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return _serialize_address(address)


@router.delete("/{user_id}/{address_id}", response_model=ActionStatusResponse)
async def delete_address(
    user_id: int,
    address_id: int,
    session: AsyncSession = Depends(service_session),
) -> ActionStatusResponse:
    service = AddressService(session)
    address = await _get_owned_address_or_404(service, user_id, address_id)

    client = await service.clients.get_by_user_id(user_id)
    await service.delete_address(address_id)

    await emit_client_log(
        "remove_address",
        client,
        actor_id=user_id,
        address_name=address.label,
        address=address.full_address,
    )
    return ActionStatusResponse()
