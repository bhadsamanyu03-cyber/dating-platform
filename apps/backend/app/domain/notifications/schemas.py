from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: UUID
    recipient_id: UUID
    actor_id: UUID | None
    type: str
    payload: dict
    is_read: bool
    created_at: datetime


class NotificationPage(BaseModel):
    notifications: list[NotificationResponse]
    next_cursor: str | None


class UnreadNotificationCount(BaseModel):
    count: int
