from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.profile.models import Interest, UserProfile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def by_user(self, user_id: UUID) -> UserProfile | None:
        return await self.db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))

    async def by_username(self, username: str) -> UserProfile | None:
        return await self.db.scalar(select(UserProfile).where(UserProfile.username == username))

    async def interests(self, ids: list[UUID] | None = None) -> list[Interest]:
        query = select(Interest).order_by(Interest.name)
        if ids is not None:
            query = query.where(Interest.id.in_(ids))
        return list(await self.db.scalars(query))
