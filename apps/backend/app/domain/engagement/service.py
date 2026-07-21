from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.engagement.models import PostComment
from app.domain.engagement.repository import EngagementRepository
from app.domain.engagement.schemas import CommentCreate, CommentPage, CommentResponse
from app.domain.identity.security import utcnow
from app.domain.notifications.repository import decode_cursor, encode_cursor
from app.domain.notifications.service import NotificationService


class EngagementError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status_code = message, status


class EngagementService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, EngagementRepository(db)

    async def valid_post(self, id):
        post = await self.repo.post(id)
        if not post:
            raise EngagementError("Post not found", 404)
        return post

    async def like(self, post, user):
        value = await self.valid_post(post)
        if not await self.repo.like(post, user):
            raise EngagementError("Post already liked", 409)
        if value.author_user_id != user:
            await NotificationService(self.db).create(
                value.author_user_id, user, "POST_LIKE", {"post_id": str(post)}
            )
        await self.db.commit()

    async def unlike(self, post, user):
        await self.valid_post(post)
        await self.repo.unlike(post, user)
        await self.db.commit()

    async def create_comment(self, post, user, payload: CommentCreate):
        target = await self.valid_post(post)
        if not payload.body.strip():
            raise EngagementError("Comment body is required", 422)
        value = PostComment(post_id=post, author_user_id=user, body=payload.body.strip())
        await self.repo.comment(value)
        if target.author_user_id != user:
            await NotificationService(self.db).create(
                target.author_user_id,
                user,
                "POST_COMMENT",
                {"post_id": str(post), "comment_id": str(value.id)},
            )
        await self.db.commit()
        await self.db.refresh(value)
        return CommentResponse(
            id=value.id,
            author_user_id=value.author_user_id,
            body=value.body,
            created_at=value.created_at,
        )

    async def comments(self, post, cursor: str | None, limit: int):
        await self.valid_post(post)
        values = await self.repo.comments(post, decode_cursor(cursor), limit)
        page = values[:limit]
        return CommentPage(
            comments=[
                CommentResponse(
                    id=x.id, author_user_id=x.author_user_id, body=x.body, created_at=x.created_at
                )
                for x in page
            ],
            next_cursor=encode_cursor(page[-1]) if len(values) > limit and page else None,
        )

    async def counts(self, post):
        await self.valid_post(post)
        return await self.repo.counts(post)

    async def delete_comment(self, id, user):
        value = await self.repo.owned_comment(id, user)
        if not value:
            raise EngagementError("Comment not found", 404)
        value.deleted_at = utcnow()
        await self.db.commit()
