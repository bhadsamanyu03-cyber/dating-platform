import base64
import binascii
import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notifications.models import Notification


def encode_cursor(notification: Notification) -> str:
    return base64.urlsafe_b64encode(
        json.dumps([notification.created_at.isoformat(), str(notification.id)]).encode()
    ).decode()


def decode_cursor(cursor: str | None) -> tuple[datetime, UUID] | None:
    if not cursor:
        return None
    try:
        created_at, notification_id = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return datetime.fromisoformat(created_at), UUID(notification_id)
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError):
        raise ValueError("Invalid cursor") from None


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, recipient_id: UUID, actor_id: UUID | None, type: str, payload: dict
    ) -> Notification:
        value = Notification(
            recipient_id=recipient_id, actor_id=actor_id, type=type, payload=payload
        )
        self.db.add(value)
        await self.db.flush()
        return value

    async def list_for_recipient(
        self, recipient_id: UUID, cursor: tuple[datetime, UUID] | None, limit: int
    ) -> list[Notification]:
        query = select(Notification).where(Notification.recipient_id == recipient_id)
        if cursor:
            created_at, notification_id = cursor
            query = query.where(
                or_(
                    Notification.created_at < created_at,
                    and_(Notification.created_at == created_at, Notification.id < notification_id),
                )
            )
        return list(
            (
                await self.db.scalars(
                    query.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(
                        limit + 1
                    )
                )
            ).all()
        )

    async def unread_count(self, recipient_id: UUID) -> int:
        return int(
            await self.db.scalar(
                select(func.count())
                .select_from(Notification)
                .where(Notification.recipient_id == recipient_id, Notification.is_read.is_(False))
            )
            or 0
        )

    async def mark_read(self, notification_id: UUID, recipient_id: UUID) -> bool:
        result = await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id, Notification.recipient_id == recipient_id)
            .values(is_read=True)
        )
        return result.rowcount > 0

    async def mark_all_read(self, recipient_id: UUID) -> None:
        await self.db.execute(
            update(Notification)
            .where(Notification.recipient_id == recipient_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
