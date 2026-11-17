from __future__ import annotations

from services.support.service import SupportService
from shared.bot.session import resolve_session
from .exceptions import ApiNotFoundError
from .schemas import (
    ActionStatusResponse,
    AgreementItem,
    AgreementsResponse,
    MessageCountResponse,
    SupportClientSummary,
    SupportMessage,
    SupportThread,
)


class SupportApi:
    async def bootstrap_client(
        self,
        *,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ) -> None:
        async with resolve_session() as session:
            ss = SupportService(session)
            await ss.clients.get_or_create(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )

    async def list_agreements(self) -> AgreementsResponse:
        async with resolve_session() as session:
            ss = SupportService(session)
            agreements = await ss.agreements.get_all()
            return AgreementsResponse(
                items=[
                    AgreementItem(
                        agreement_id=a.agreement_id,
                        title=a.title,
                        document_url=a.document_url,
                    )
                    for a in agreements
                ]
            )

    async def get_client_summary(self, user_id: int) -> SupportClientSummary:
        async with resolve_session() as session:
            ss = SupportService(session)
            summary = await ss.get_client_summary(user_id)
            if not summary or not summary.get("client"):
                raise ApiNotFoundError(f"Client not found: {user_id}")
            client = summary["client"]
            agreement = summary.get("agreement")
            thread = summary.get("thread")
            return SupportClientSummary(
                user_id=client.user_id,
                first_name=client.first_name,
                last_name=client.last_name,
                username=client.username,
                primary_city=client.primary_city,
                secondary_city=client.secondary_city,
                active_city_slot=int(getattr(client, "active_city_slot", 1) or 1),
                promo=client.promo_code,
                is_banned=bool(getattr(thread, "is_banned", False) or getattr(client, "is_banned", False)),
                title=agreement.title if agreement else None,
                forum_chat_id=thread.forum_chat_id if thread else None,
                topic_id=thread.forum_topic_id if thread else None,
                registered_at=client.registered_at,
            )

    async def set_client_agreement(self, user_id: int, agreement_id: str) -> None:
        async with resolve_session() as session:
            ss = SupportService(session)
            await ss.clients.set_agreement(user_id, agreement_id)

    async def get_thread_by_user(self, user_id: int) -> SupportThread:
        async with resolve_session() as session:
            ss = SupportService(session)
            thread = await ss.threads.get_by_user(user_id)
            if not thread:
                raise ApiNotFoundError(f"Support thread not found for user: {user_id}")
            return SupportThread(
                user_id=thread.user_id,
                forum_chat_id=thread.forum_chat_id,
                topic_id=thread.forum_topic_id,
                info_message_id=thread.pinned_info_message_id,
                is_banned=bool(thread.is_banned),
            )

    async def get_thread_by_topic(self, *, forum_chat_id: int, topic_id: int) -> SupportThread:
        async with resolve_session() as session:
            ss = SupportService(session)
            thread = await ss.threads.get_by_topic(forum_chat_id, topic_id)
            if not thread:
                raise ApiNotFoundError(f"Support thread not found for topic: {topic_id}")
            return SupportThread(
                user_id=thread.user_id,
                forum_chat_id=thread.forum_chat_id,
                topic_id=thread.forum_topic_id,
                info_message_id=thread.pinned_info_message_id,
                is_banned=bool(thread.is_banned),
            )

    async def upsert_thread(
        self,
        *,
        user_id: int,
        forum_chat_id: int,
        topic_id: int,
        info_message_id: int | None = None,
    ) -> SupportThread:
        async with resolve_session() as session:
            ss = SupportService(session)
            thread = await ss.threads.upsert_thread(
                user_id=user_id,
                forum_chat_id=forum_chat_id,
                topic_id=topic_id,
                info_message_id=info_message_id,
            )
            return SupportThread(
                user_id=thread.user_id,
                forum_chat_id=thread.forum_chat_id,
                topic_id=thread.forum_topic_id,
                info_message_id=thread.pinned_info_message_id,
                is_banned=bool(thread.is_banned),
            )

    async def set_ban(self, *, user_id: int, is_banned: bool) -> SupportThread:
        async with resolve_session() as session:
            ss = SupportService(session)
            thread = await ss.threads.get_by_user(user_id)
            if thread:
                thread.is_banned = is_banned
            client = await ss.clients.get(user_id)
            if client:
                client.is_banned = is_banned
            if not thread:
                raise ApiNotFoundError(f"Support thread not found for user: {user_id}")
            return SupportThread(
                user_id=thread.user_id,
                forum_chat_id=thread.forum_chat_id,
                topic_id=thread.forum_topic_id,
                info_message_id=thread.pinned_info_message_id,
                is_banned=bool(thread.is_banned),
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
        async with resolve_session() as session:
            ss = SupportService(session)
            msg = await ss.messages.create(
                user_id=user_id,
                forum_chat_id=forum_chat_id,
                forum_topic_id=topic_id,
                forum_message_id=support_message_id,
                client_message_id=user_message_id,
            )
            return SupportMessage(
                id=msg.id,
                user_id=msg.user_id,
                forum_chat_id=msg.forum_chat_id,
                topic_id=msg.forum_topic_id,
                support_message_id=msg.forum_message_id,
                user_message_id=msg.client_message_id,
            )

    async def get_message_by_support(self, *, forum_chat_id: int, support_message_id: int) -> SupportMessage:
        async with resolve_session() as session:
            ss = SupportService(session)
            msg = await ss.messages.get_by_support_message(forum_chat_id, support_message_id)
            if not msg:
                raise ApiNotFoundError("Support message not found")
            return SupportMessage(
                id=msg.id,
                user_id=msg.user_id,
                forum_chat_id=msg.forum_chat_id,
                topic_id=msg.forum_topic_id,
                support_message_id=msg.forum_message_id,
                user_message_id=msg.client_message_id,
            )

    async def get_message_by_user(self, *, user_id: int, user_message_id: int) -> SupportMessage:
        async with resolve_session() as session:
            ss = SupportService(session)
            msg = await ss.messages.get_by_user_message(user_id, user_message_id)
            if not msg:
                raise ApiNotFoundError("User message not found")
            return SupportMessage(
                id=msg.id,
                user_id=msg.user_id,
                forum_chat_id=msg.forum_chat_id,
                topic_id=msg.forum_topic_id,
                support_message_id=msg.forum_message_id,
                user_message_id=msg.client_message_id,
            )

    async def count_user_messages(self, user_id: int) -> int:
        async with resolve_session() as session:
            ss = SupportService(session)
            return await ss.count_user_messages(user_id)
