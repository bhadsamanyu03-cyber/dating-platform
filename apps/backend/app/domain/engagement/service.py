from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.engagement.models import PostComment
from app.domain.engagement.repository import EngagementRepository
from app.domain.engagement.schemas import CommentCreate, CommentPage, CommentResponse
from app.domain.identity.security import utcnow


class EngagementError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status_code = message, status


class EngagementService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, EngagementRepository(db)

    async def valid_post(self, id):
        if not await self.repo.post(id):
            raise EngagementError("Post not found", 404)

    async def like(self, post, user):
        await self.valid_post(post)
        await self.repo.like(post, user)
        await self.db.commit()

    async def unlike(self, post, user):
        await self.valid_post(post)
        await self.repo.unlike(post, user)
        await self.db.commit()

    async def create_comment(self, post, user, payload: CommentCreate):
        await self.valid_post(post)
        if not payload.body.strip():
            raise EngagementError("Comment body is required", 422)
        value = PostComment(post_id=post, author_user_id=user, body=payload.body.strip())
        await self.repo.comment(value)
        await self.db.commit()
        await self.db.refresh(value)
        return CommentResponse(
            id=value.id,
            author_user_id=value.author_user_id,
            body=value.body,
            created_at=value.created_at,
        )

    async def comments(self, post):
        await self.valid_post(post)
        return CommentPage(
            comments=[
                CommentResponse(
                    id=x.id, author_user_id=x.author_user_id, body=x.body, created_at=x.created_at
                )
                for x in await self.repo.comments(post)
            ],
            next_cursor=None,
        )

    async def delete_comment(self, id, user):
        value = await self.repo.owned_comment(id, user)
        if not value:
            raise EngagementError("Comment not found", 404)
        value.deleted_at = utcnow()
        await self.db.commit()
