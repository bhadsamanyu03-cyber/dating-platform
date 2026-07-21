from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.media.models import MediaAsset
from app.domain.profile.models import Interest, ProfilePhoto, UserProfile


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

    async def owned_image_asset(self, asset_id: UUID, user_id: UUID) -> MediaAsset | None:
        return await self.db.scalar(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.owner_user_id == user_id,
                MediaAsset.media_type == "IMAGE",
                MediaAsset.upload_status == "UPLOADED",
            )
        )

    async def photos(self, profile_id: UUID) -> list[ProfilePhoto]:
        return list(
            await self.db.scalars(
                select(ProfilePhoto)
                .where(ProfilePhoto.profile_id == profile_id)
                .order_by(ProfilePhoto.ordering, ProfilePhoto.created_at)
            )
        )

    async def photo(self, profile_id: UUID, photo_id: UUID) -> ProfilePhoto | None:
        return await self.db.scalar(
            select(ProfilePhoto).where(
                ProfilePhoto.profile_id == profile_id, ProfilePhoto.id == photo_id
            )
        )

    async def primary_photo(self, profile_id: UUID) -> ProfilePhoto | None:
        return await self.db.scalar(
            select(ProfilePhoto).where(
                ProfilePhoto.profile_id == profile_id, ProfilePhoto.is_primary.is_(True)
            )
        )

    async def clear_primary(self, profile_id: UUID) -> None:
        await self.db.execute(
            update(ProfilePhoto)
            .where(ProfilePhoto.profile_id == profile_id, ProfilePhoto.is_primary.is_(True))
            .values(is_primary=False)
        )
