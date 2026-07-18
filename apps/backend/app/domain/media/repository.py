from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.media.models import MediaAsset


class MediaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def owned(self, asset_id: UUID, owner: UUID):
        return await self.db.scalar(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.owner_user_id == owner,
                MediaAsset.upload_status != "DELETED",
            )
        )

    async def add(self, asset: MediaAsset):
        self.db.add(asset)
        await self.db.flush()
