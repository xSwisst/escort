from __future__ import annotations

from clients.logs import emit_log_event
from services.addresses.service import AddressService
from services.clients.service import ClientService
from shared.bot.session import resolve_session
from .exceptions import ApiNotFoundError
from .schemas import ActionStatusResponse, AddressItem, AddressListResponse


class AddressesApi:
    async def list(self, user_id: int) -> AddressListResponse:
        async with resolve_session() as session:
            addr_service = AddressService(session)
            addrs = await addr_service.list(user_id)
            return AddressListResponse(
                items=[
                    AddressItem(
                        id=a.id,
                        user_id=a.user_id,
                        title=a.title,
                        address=a.address,
                        created_at=a.created_at,
                    )
                    for a in addrs
                ]
            )

    async def get(self, *, user_id: int, address_id: int) -> AddressItem:
        async with resolve_session() as session:
            addr_service = AddressService(session)
            a = await addr_service.get(user_id, address_id)
            if not a:
                raise ApiNotFoundError(f"Address not found: {address_id}")
            return AddressItem(
                id=a.id,
                user_id=a.user_id,
                title=a.title,
                address=a.address,
                created_at=a.created_at,
            )

    async def create(self, *, user_id: int, title: str, address: str) -> AddressItem:
        async with resolve_session() as session:
            addr_service = AddressService(session)
            a = await addr_service.create(user_id, title=title, address=address)
            client = await ClientService(session).get_client(user_id)
            if client:
                await emit_log_event(
                    "add_address",
                    user_id,
                    {
                        "id": client.id,
                        "user_id": client.user_id,
                        "first_name": client.first_name or "",
                        "last_name": client.last_name or "",
                        "username": client.username,
                        "admin_id": client.admin_id,
                        "address_name": title,
                        "address": address,
                    },
                )
            return AddressItem(
                id=a.id,
                user_id=a.user_id,
                title=a.title,
                address=a.address,
                created_at=a.created_at,
            )

    async def update_title(self, *, user_id: int, address_id: int, title: str) -> AddressItem:
        async with resolve_session() as session:
            addr_service = AddressService(session)
            a = await addr_service.update_title(user_id, address_id, title)
            if not a:
                raise ApiNotFoundError(f"Address not found: {address_id}")
            return AddressItem(
                id=a.id,
                user_id=a.user_id,
                title=a.title,
                address=a.address,
                created_at=a.created_at,
            )

    async def update_address(self, *, user_id: int, address_id: int, address: str) -> AddressItem:
        async with resolve_session() as session:
            addr_service = AddressService(session)
            a = await addr_service.update_address_text(user_id, address_id, address)
            if not a:
                raise ApiNotFoundError(f"Address not found: {address_id}")
            return AddressItem(
                id=a.id,
                user_id=a.user_id,
                title=a.title,
                address=a.address,
                created_at=a.created_at,
            )

    async def delete(self, *, user_id: int, address_id: int) -> None:
        async with resolve_session() as session:
            addr_service = AddressService(session)
            existing = await addr_service.get(user_id, address_id)
            ok = await addr_service.delete(user_id, address_id)
            if not ok:
                raise ApiNotFoundError(f"Address not found: {address_id}")
            client = await ClientService(session).get_client(user_id)
            if client and existing:
                await emit_log_event(
                    "remove_address",
                    user_id,
                    {
                        "id": client.id,
                        "user_id": client.user_id,
                        "first_name": client.first_name or "",
                        "last_name": client.last_name or "",
                        "username": client.username,
                        "admin_id": client.admin_id,
                        "address_name": existing.title,
                        "address": existing.address,
                    },
                )
