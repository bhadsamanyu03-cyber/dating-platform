from uuid import UUID
from datetime import datetime
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.engagement.models import PostComment, PostLike
from app.domain.feed.models import Post


class EngagementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def post(self, id: UUID):
        return await self.db.scalar(select(Post).where(Post.id == id, Post.deleted_at.is_(None)))

    async def like(self, post: UUID, user: UUID) -> bool:
        result = await self.db.execute(
            insert(PostLike)
            .values(post_id=post, user_id=user)
            .on_conflict_do_nothing()
            .returning(PostLike.id)
        )
        return result.scalar_one_or_none() is not None

    async def unlike(self, post: UUID, user: UUID):
        await self.db.execute(
            delete(PostLike).where(PostLike.post_id == post, PostLike.user_id == user)
        )

    async def comment(self, value):
        self.db.add(value)
        await self.db.flush()

    async def comments(self, post: UUID, cursor: tuple[datetime, UUID] | None, limit: int):
        query = select(PostComment).where(
            PostComment.post_id == post, PostComment.deleted_at.is_(None)
        )
        if cursor:
            created_at, comment_id = cursor
            query = query.where(
                or_(
                    PostComment.created_at < created_at,
                    and_(PostComment.created_at == created_at, PostComment.id < comment_id),
                )
            )
        return list(
            (
                await self.db.scalars(
                    query.order_by(PostComment.created_at.desc(), PostComment.id.desc()).limit(
                        limit + 1
                    )
                )
            ).all()
        )

    async def counts(self, post: UUID) -> tuple[int, int]:
        likes = await self.db.scalar(
            select(func.count()).select_from(PostLike).where(PostLike.post_id == post)
        )
        comments = await self.db.scalar(
            select(func.count())
            .select_from(PostComment)
            .where(PostComment.post_id == post, PostComment.deleted_at.is_(None))
        )
        return int(likes or 0), int(comments or 0)

    async def owned_comment(self, id: UUID, user: UUID):
        return await self.db.scalar(
            select(PostComment).where(
                PostComment.id == id,
                PostComment.author_user_id == user,
                PostComment.deleted_at.is_(None),
            )
        )
