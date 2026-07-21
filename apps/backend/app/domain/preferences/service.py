from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.discovery.schemas import DiscoveryFilters
from app.domain.preferences.models import DiscoveryPreference, PreferredGender
from app.domain.preferences.repository import DiscoveryPreferenceRepository
from app.domain.preferences.schemas import DiscoveryPreferenceResponse, DiscoveryPreferenceUpdate


class DiscoveryPreferenceService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, DiscoveryPreferenceRepository(db)

    @staticmethod
    def response(value: DiscoveryPreference) -> DiscoveryPreferenceResponse:
        return DiscoveryPreferenceResponse(
            preferred_gender=PreferredGender(value.preferred_gender),
            minimum_age=value.minimum_age,
            maximum_age=value.maximum_age,
            maximum_distance_km=value.maximum_distance_km,
            show_verified_only=value.show_verified_only,
            show_only_with_photos=value.show_only_with_photos,
            created_at=value.created_at,
            updated_at=value.updated_at,
        )

    async def get(self, user_id: UUID) -> DiscoveryPreferenceResponse:
        value = await self.repo.by_user(user_id)
        if value is None:
            value = await self.repo.create(DiscoveryPreference(user_id=user_id))
            await self.db.commit()
            await self.db.refresh(value)
        return self.response(value)

    async def update(
        self, user_id: UUID, payload: DiscoveryPreferenceUpdate
    ) -> DiscoveryPreferenceResponse:
        value = await self.repo.by_user(user_id)
        if value is None:
            value = DiscoveryPreference(user_id=user_id)
            await self.repo.create(value)
        for key, item in payload.model_dump().items():
            setattr(value, key, item.value if isinstance(item, PreferredGender) else item)
        await self.db.commit()
        await self.db.refresh(value)
        return self.response(value)

    async def filters(self, user_id: UUID) -> DiscoveryFilters:
        value = await self.repo.by_user(user_id)
        if value is None:
            return DiscoveryFilters()
        return DiscoveryFilters(
            gender=(
                None
                if value.preferred_gender == PreferredGender.ALL.value
                else value.preferred_gender
            ),
            min_age=value.minimum_age,
            max_age=value.maximum_age,
            verified_only=value.show_verified_only,
            show_only_with_photos=value.show_only_with_photos,
        )
