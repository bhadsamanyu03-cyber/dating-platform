from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notifications.models import Notification
from app.domain.notifications.repository import NotificationRepository, decode_cursor, encode_cursor
from app.domain.notifications.schemas import (
    NotificationPage,
    NotificationResponse,
    UnreadNotificationCount,
)


class NotificationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message, self.status_code = message, status_code


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, NotificationRepository(db)

    @staticmethod
    def response(value: Notification) -> NotificationResponse:
        return NotificationResponse(
            id=value.id,
            recipient_id=value.recipient_id,
            actor_id=value.actor_id,
            type=value.type,
            payload=value.payload,
            is_read=value.is_read,
            created_at=value.created_at,
        )

    async def create(
        self, recipient_id: UUID, actor_id: UUID | None, type: str, payload: dict
    ) -> Notification:
        return await self.repo.create(recipient_id, actor_id, type, payload)

    async def list(self, recipient_id: UUID, cursor: str | None, limit: int) -> NotificationPage:
        values = await self.repo.list_for_recipient(recipient_id, decode_cursor(cursor), limit)
        page = values[:limit]
        return NotificationPage(
            notifications=[self.response(value) for value in page],
            next_cursor=encode_cursor(page[-1]) if len(values) > limit and page else None,
        )

    async def unread_count(self, recipient_id: UUID) -> UnreadNotificationCount:
        return UnreadNotificationCount(count=await self.repo.unread_count(recipient_id))

    async def mark_read(self, notification_id: UUID, recipient_id: UUID) -> None:
        if not await self.repo.mark_read(notification_id, recipient_id):
            raise NotificationError("Notification not found", 404)
        await self.db.commit()

    async def mark_all_read(self, recipient_id: UUID) -> None:
        await self.repo.mark_all_read(recipient_id)
        await self.db.commit()
