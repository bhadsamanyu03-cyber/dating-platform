from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.feed.models import Post, PostMedia
from app.domain.feed.repository import FeedRepository
from app.domain.feed.schemas import PostCreate, PostPage, PostResponse
from app.domain.notifications.repository import decode_cursor, encode_cursor


class FeedError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status_code = message, status


class FeedService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, FeedRepository(db)

    async def response(self, post, media=None, counts=None):
        like_count, comment_count = counts or await self.repo.counts(post.id)
        return PostResponse(
            id=post.id,
            author_user_id=post.author_user_id,
            caption=post.caption,
            visibility=post.visibility,
            media_asset_ids=[
                x.media_asset_id
                for x in (media if media is not None else await self.repo.media(post.id))
            ],
            like_count=like_count,
            comment_count=comment_count,
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

    async def list(self, user: UUID, cursor: str | None, limit: int, author: UUID | None = None):
        values = await self.repo.list(user, author, decode_cursor(cursor), limit)
        page = values[:limit]
        ids = [post.id for post in page]
        media = await self.repo.media_for_posts(ids)
        counts = await self.repo.counts_for_posts(ids)
        return PostPage(
            posts=[
                await self.response(post, media.get(post.id), counts.get(post.id)) for post in page
            ],
            next_cursor=encode_cursor(page[-1]) if len(values) > limit and page else None,
        )

    async def delete(self, id: UUID, user: UUID):
        post = await self.repo.post(id, user)
        if not post or post.author_user_id != user:
            raise FeedError("Post not found", 404)
        from app.domain.identity.security import utcnow

        post.deleted_at = utcnow()
        await self.db.commit()
