from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Identity, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.utils.time import now_msk
from shared.db import Base


class Form(Base):
    """
    Core form entity - contains only identity and aggregated metrics.

    Profile data, pricing, and publication settings are in separate tables
    for better separation of concerns and query performance.
    """
    __tablename__ = "forms"

    id: Mapped[int] = mapped_column(Integer, Identity(), nullable=False, unique=True, index=True)
    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    # Aggregated metrics (frequently queried, rarely updated)
    orders_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    profile: Mapped["FormProfile"] = relationship("FormProfile", back_populates="form", cascade="all, delete-orphan", uselist=False)
    pricing: Mapped["FormPricing"] = relationship("FormPricing", back_populates="form", cascade="all, delete-orphan", uselist=False)
    publication: Mapped["FormPublication"] = relationship("FormPublication", back_populates="form", cascade="all, delete-orphan", uselist=False)

    reviews: Mapped[list["FormReview"]] = relationship("FormReview", back_populates="form", cascade="all, delete-orphan")
    services: Mapped[list["FormService"]] = relationship("FormService", back_populates="form", cascade="all, delete-orphan")
    additionals: Mapped[list["FormAdditional"]] = relationship("FormAdditional", back_populates="form", cascade="all, delete-orphan")
    photos: Mapped[list["FormPhoto"]] = relationship(
        "FormPhoto",
        back_populates="form",
        cascade="all, delete-orphan",
        order_by="FormPhoto.sort_order.asc()",
    )
    favorites: Mapped[list["FormFavorite"]] = relationship("FormFavorite", back_populates="form", cascade="all, delete-orphan")
    private_channel: Mapped["FormPrivateChannel | None"] = relationship(
        "FormPrivateChannel",
        back_populates="form",
        cascade="all, delete-orphan",
        uselist=False,
    )


class FormProfile(Base):
    """
    Form profile data - public biographical and physical characteristics.

    This is the most frequently read data when displaying form cards.
    """
    __tablename__ = "forms_profiles"

    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    bust_size: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    @property
    def caption(self) -> str | None:
        return self.description

    @caption.setter
    def caption(self, value: str | None) -> None:
        self.description = value

    form: Mapped["Form"] = relationship("Form", back_populates="profile")


class FormPricing(Base):
    """
    Form pricing data - service duration prices.

    Separated for independent updates and clear business domain boundary.
    """
    __tablename__ = "forms_pricing"

    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    one_hour_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    two_hour_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    three_hour_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overnight_price: Mapped[int | None] = mapped_column(Integer, nullable=True)

    form: Mapped["Form"] = relationship("Form", back_populates="pricing")


class FormPublication(Base):
    """
    Form publication and moderation data.

    Controls visibility, verification status, and display ordering.
    Updated by admins and moderation workflows.
    """
    __tablename__ = "forms_publication"

    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_medical_certificate: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    public_channel_url: Mapped[str | None] = mapped_column(String(256), nullable=True)
    city_slot: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    form: Mapped["Form"] = relationship("Form", back_populates="publication")


class FormReview(Base):
    __tablename__ = "forms_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    author: Mapped[str | None] = mapped_column(String(128), nullable=True)
    review_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    form: Mapped["Form"] = relationship("Form", back_populates="reviews")


class FormAdditional(Base):
    __tablename__ = "forms_additionals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    form: Mapped["Form"] = relationship("Form", back_populates="additionals")


class FormPhoto(Base):
    __tablename__ = "forms_photos"
    __table_args__ = (UniqueConstraint("form_code", "storage_key", name="uq_forms_photos_form_file"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    form: Mapped["Form"] = relationship("Form", back_populates="photos")


class FormService(Base):
    __tablename__ = "forms_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    name: Mapped[str] = mapped_column(String(128), nullable=False)

    form: Mapped["Form"] = relationship("Form", back_populates="services")


class FormFavorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "form_code", name="uq_favorites_user_form"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.user_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)

    form: Mapped["Form"] = relationship("Form", back_populates="favorites")
    client: Mapped["Client"] = relationship("Client", back_populates="favorite_forms")


class FormPrivateChannel(Base):
    __tablename__ = "forms_private_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_code: Mapped[str] = mapped_column(String(64), ForeignKey("forms.code", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=now_msk, onupdate=now_msk, server_default=func.now(), nullable=False)

    subscription_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    form: Mapped["Form"] = relationship("Form", back_populates="private_channel")
