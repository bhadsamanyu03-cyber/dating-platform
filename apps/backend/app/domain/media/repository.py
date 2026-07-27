from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.media.models import MediaAsset, MediaVariant


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

    async def by_id(self, asset_id: UUID) -> MediaAsset | None:
        return await self.db.scalar(select(MediaAsset).where(MediaAsset.id == asset_id))

    async def by_storage_key(self, storage_key: str) -> MediaAsset | None:
        return await self.db.scalar(select(MediaAsset).where(MediaAsset.storage_key == storage_key))

    async def add(self, asset: MediaAsset):
        self.db.add(asset)
        await self.db.flush()

    async def add_variant(self, variant: MediaVariant) -> None:
        self.db.add(variant)
        await self.db.flush()

    async def has_variants(self, asset_id: UUID) -> bool:
        return bool(
            await self.db.scalar(
                select(MediaVariant.id).where(MediaVariant.media_asset_id == asset_id).limit(1)
            )
        )

    async def stale_processing(self, before: datetime) -> list[MediaAsset]:
        return list(
            await self.db.scalars(
                select(MediaAsset).where(
                    MediaAsset.processing_state.in_(["QUEUED", "PROCESSING"]),
                    MediaAsset.updated_at < before,
                )
            )
        )

    async def variants(self, asset_id: UUID) -> list[MediaVariant]:
        return list(
            await self.db.scalars(
                select(MediaVariant)
                .where(MediaVariant.media_asset_id == asset_id)
                .order_by(MediaVariant.kind)
            )
        )
