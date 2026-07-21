import uuid
from datetime import date, datetime
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.identity.models import Base

profile_interests = Table(
    "profile_interests",
    Base.metadata,
    Column(
        "profile_id",
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "interest_id",
        UUID(as_uuid=True),
        ForeignKey("interests.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Interest(Base):
    __tablename__ = "interests"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    gender: Mapped[str] = mapped_column(String(100))
    pronouns: Mapped[str | None] = mapped_column(String(100))
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    height_cm: Mapped[int | None] = mapped_column(Integer)
    profile_photo_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    profile_video_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_discoverable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    profile_completion_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    interests: Mapped[list[Interest]] = relationship(secondary=profile_interests, lazy="selectin")
    photos: Mapped[list["ProfilePhoto"]] = relationship(
        order_by="ProfilePhoto.ordering", cascade="all, delete-orphan"
    )


class ProfilePhoto(Base):
    __tablename__ = "profile_photos"
    __table_args__ = (
        Index("uq_profile_photos_profile_asset", "profile_id", "media_asset_id", unique=True),
        Index("ix_profile_photos_profile_ordering", "profile_id", "ordering"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE")
    )
    media_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("media_assets.id", ondelete="RESTRICT")
    )
    ordering: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
