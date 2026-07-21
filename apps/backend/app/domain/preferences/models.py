import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.identity.models import Base


class PreferredGender(StrEnum):
    ALL = "All"
    WOMAN = "Woman"
    MAN = "Man"
    NON_BINARY = "Non-binary"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


class DiscoveryPreference(Base):
    __tablename__ = "discovery_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    preferred_gender: Mapped[str] = mapped_column(
        String(100), default=PreferredGender.ALL.value, nullable=False
    )
    minimum_age: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    maximum_age: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    maximum_distance_km: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    show_verified_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_only_with_photos: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
