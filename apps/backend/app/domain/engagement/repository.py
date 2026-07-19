from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.engagement.models import PostComment, PostLike
from app.domain.feed.models import Post


class EngagementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def post(self, id: UUID):
        return await self.db.scalar(select(Post).where(Post.id == id, Post.deleted_at.is_(None)))

    async def like(self, post: UUID, user: UUID):
        await self.db.execute(
            insert(PostLike).values(post_id=post, user_id=user).on_conflict_do_nothing()
        )

    async def unlike(self, post: UUID, user: UUID):
        await self.db.execute(
            delete(PostLike).where(PostLike.post_id == post, PostLike.user_id == user)
        )

    async def comment(self, value):
        self.db.add(value)
        await self.db.flush()

    async def comments(self, post: UUID):
        return list(
            (
                await self.db.scalars(
                    select(PostComment)
                    .where(PostComment.post_id == post, PostComment.deleted_at.is_(None))
                    .order_by(PostComment.created_at.desc())
                    .limit(50)
                )
            ).all()
        )

    async def owned_comment(self, id: UUID, user: UUID):
        return await self.db.scalar(
            select(PostComment).where(
                PostComment.id == id,
                PostComment.author_user_id == user,
                PostComment.deleted_at.is_(None),
            )
        )
