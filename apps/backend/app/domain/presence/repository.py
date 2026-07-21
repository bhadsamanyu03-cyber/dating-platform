from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.presence.models import UserPresence


class PresenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: UUID) -> UserPresence | None:
        return await self.db.scalar(select(UserPresence).where(UserPresence.user_id == user_id))

    async def create(self, value: UserPresence) -> UserPresence:
        self.db.add(value)
        await self.db.flush()
        return value
