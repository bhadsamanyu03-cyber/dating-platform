from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.feed.models import Post, PostMedia
from app.domain.feed.repository import FeedRepository
from app.domain.feed.schemas import PostCreate, PostPage, PostResponse


class FeedError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status_code = message, status


class FeedService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, FeedRepository(db)

    async def response(self, post):
        return PostResponse(
            id=post.id,
            author_user_id=post.author_user_id,
            caption=post.caption,
            visibility=post.visibility,
            media_asset_ids=[x.media_asset_id for x in await self.repo.media(post.id)],
            created_at=post.created_at,
        )

    async def create(self, user: UUID, payload: PostCreate):
        if len(await self.repo.assets(payload.media_asset_ids, user)) != len(
            payload.media_asset_ids
        ):
            raise FeedError("Invalid media asset", 422)
        post = Post(author_user_id=user, caption=payload.caption, visibility=payload.visibility)
        await self.repo.add(post)
        for position, asset in enumerate(payload.media_asset_ids):
            self.db.add(PostMedia(post_id=post.id, media_asset_id=asset, position=position))
        await self.db.commit()
        await self.db.refresh(post)
        return await self.response(post)

    async def get(self, id: UUID, user: UUID | None):
        post = await self.repo.post(id, user)
        if not post:
            raise FeedError("Post not found", 404)
        return await self.response(post)

    async def list(self, user: UUID | None, author: UUID | None = None):
        return PostPage(
            posts=[await self.response(x) for x in await self.repo.list(user, author, 50)],
            next_cursor=None,
        )

    async def delete(self, id: UUID, user: UUID):
        post = await self.repo.post(id, user)
        if not post or post.author_user_id != user:
            raise FeedError("Post not found", 404)
        from app.domain.identity.security import utcnow

        post.deleted_at = utcnow()
        await self.db.commit()
