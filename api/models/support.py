from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.time_utils import now_msk
from shared.db import Base

class SupportThread(Base):
    __tablename__ = "support_threads"
    __table_args__ = (UniqueConstraint("forum_chat_id", "forum_topic_id", name="uq_support_threads_forum_topic"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    forum_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    forum_topic_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    pinned_info_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now())

    client: Mapped["Client"] = relationship("Client", back_populates="support_thread")


class SupportMessage(Base):
    __tablename__ = "support_messages"
    __table_args__ = (
        UniqueConstraint("forum_chat_id", "forum_message_id", name="uq_support_messages_forum_message"),
        UniqueConstraint("user_id", "client_message_id", name="uq_support_messages_user_message"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False, index=True)
    forum_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    forum_topic_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    forum_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    client_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    reply_to_forum_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reply_to_client_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now())

    client: Mapped["Client"] = relationship("Client", back_populates="support_messages")
