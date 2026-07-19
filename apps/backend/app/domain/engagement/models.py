import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.domain.identity.models import Base


class PostLike(Base):
    __tablename__ = "post_likes"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_like"),
        Index("ix_post_likes_post", "post_id"),
        Index("ix_post_likes_user", "user_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostComment(Base):
    __tablename__ = "post_comments"
    __table_args__ = (
        Index("ix_post_comments_post_created", "post_id", "created_at", "id"),
        Index("ix_post_comments_author", "author_user_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    author_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
