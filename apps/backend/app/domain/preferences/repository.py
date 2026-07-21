from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.preferences.models import DiscoveryPreference


class DiscoveryPreferenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def by_user(self, user_id: UUID) -> DiscoveryPreference | None:
        return await self.db.scalar(
            select(DiscoveryPreference).where(DiscoveryPreference.user_id == user_id)
        )

    async def create(self, value: DiscoveryPreference) -> DiscoveryPreference:
        self.db.add(value)
        await self.db.flush()
        return value
