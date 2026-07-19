from uuid import UUID
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.feed.models import Post, PostMedia
from app.domain.media.models import MediaAsset


class FeedRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def assets(self, ids: list[UUID], owner: UUID):
        return list(
            (
                await self.db.scalars(
                    select(MediaAsset).where(
                        MediaAsset.id.in_(ids),
                        MediaAsset.owner_user_id == owner,
                        MediaAsset.upload_status == "UPLOADED",
                    )
                )
            ).all()
        )

    async def add(self, post: Post):
        self.db.add(post)
        await self.db.flush()

    async def post(self, id: UUID, viewer: UUID | None):
        return await self.db.scalar(
            select(Post).where(
                Post.id == id,
                Post.deleted_at.is_(None),
                or_(Post.visibility == "PUBLIC", Post.author_user_id == viewer),
            )
        )

    async def media(self, id: UUID):
        return list(
            (
                await self.db.scalars(
                    select(PostMedia).where(PostMedia.post_id == id).order_by(PostMedia.position)
                )
            ).all()
        )

    async def list(self, viewer: UUID | None, author: UUID | None, limit: int):
        q = select(Post).where(
            Post.deleted_at.is_(None),
            or_(Post.visibility == "PUBLIC", Post.author_user_id == viewer),
        )
        if author:
            q = q.where(Post.author_user_id == author)
        return list(
            (
                await self.db.scalars(
                    q.order_by(Post.created_at.desc(), Post.id.desc()).limit(limit)
                )
            ).all()
        )
