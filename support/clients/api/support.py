from __future__ import annotations

from .base import ApiSection
from .schemas import ActionStatusResponse, AgreementsResponse, MessageCountResponse, SupportClientSummary, SupportMessage, SupportThread


class SupportApi(ApiSection):
    async def bootstrap_client(
        self,
        *,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ) -> None:
        await self._post(
            "/support/v1/clients/bootstrap",
            model=ActionStatusResponse,
            json={
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
            },
        )

    async def list_agreements(self) -> AgreementsResponse:
        return await self._get("/support/v1/agreements", model=AgreementsResponse)

    async def get_client_summary(self, user_id: int) -> SupportClientSummary:
        return await self._get(f"/support/v1/clients/{user_id}/summary", model=SupportClientSummary)

    async def set_client_agreement(self, user_id: int, agreement_id: str) -> None:
        await self._post(
            f"/support/v1/agreements/users/{user_id}",
            model=ActionStatusResponse,
            json={"agreement_id": agreement_id},
        )

    async def get_thread_by_user(self, user_id: int) -> SupportThread:
        return await self._get(f"/support/v1/threads/user/{user_id}", model=SupportThread)

    async def get_thread_by_topic(self, *, forum_chat_id: int, topic_id: int) -> SupportThread:
        return await self._get(
            "/support/v1/threads/topic",
            model=SupportThread,
            params={"forum_chat_id": forum_chat_id, "topic_id": topic_id},
        )

    async def upsert_thread(self, *, user_id: int, forum_chat_id: int, topic_id: int, info_message_id: int | None = None) -> SupportThread:
        return await self._put(
            f"/support/v1/threads/user/{user_id}",
            model=SupportThread,
            json={"forum_chat_id": forum_chat_id, "topic_id": topic_id, "info_message_id": info_message_id},
        )

    async def set_ban(self, *, user_id: int, is_banned: bool) -> SupportThread:
        return await self._patch(
            f"/support/v1/threads/user/{user_id}/ban",
            model=SupportThread,
            json={"is_banned": is_banned},
        )

    async def create_message_mapping(
        self,
        *,
        user_id: int,
        forum_chat_id: int,
        topic_id: int,
        support_message_id: int,
        user_message_id: int,
        original_support_message_id: int | None = None,
        original_user_message_id: int | None = None,
    ) -> SupportMessage:
        return await self._post(
            "/support/v1/messages",
            model=SupportMessage,
            json={
                "user_id": user_id,
                "forum_chat_id": forum_chat_id,
                "topic_id": topic_id,
                "support_message_id": support_message_id,
                "user_message_id": user_message_id,
                "original_support_message_id": original_support_message_id,
                "original_user_message_id": original_user_message_id,
            },
        )

    async def get_message_by_support(self, *, forum_chat_id: int, support_message_id: int) -> SupportMessage:
        return await self._get(
            "/support/v1/messages/support",
            model=SupportMessage,
            params={"forum_chat_id": forum_chat_id, "support_message_id": support_message_id},
        )

    async def get_message_by_user(self, *, user_id: int, user_message_id: int) -> SupportMessage:
        return await self._get(
            "/support/v1/messages/user",
            model=SupportMessage,
            params={"user_id": user_id, "user_message_id": user_message_id},
        )

    async def count_user_messages(self, user_id: int) -> int:
        """Count total messages sent by user to support"""
        response = await self._get(
            f"/support/v1/messages/user/{user_id}/count",
            model=MessageCountResponse,
        )
        if isinstance(response, MessageCountResponse):
            return response.count
        if isinstance(response, dict):
            return response.get("count", 0)
        return getattr(response, "count", 0)
