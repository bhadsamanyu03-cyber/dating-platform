from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.discovery.models import ProfileLike, ProfilePass
from app.domain.discovery.repository import DiscoveryRepository, decode_cursor, encode_cursor
from app.domain.discovery.schemas import DiscoveryPage, DiscoveryProfile
from app.domain.identity.models import User
from app.domain.profile.schemas import InterestResponse


class DiscoveryError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message, self.status_code = message, status_code


class RankingStrategy:
    def profile(self, value) -> DiscoveryProfile:
        return DiscoveryProfile(
            user_id=value.user_id,
            username=value.username,
            display_name=value.display_name,
            bio=value.bio,
            gender=value.gender,
            pronouns=value.pronouns,
            age=date.today().year
            - value.date_of_birth.year
            - (
                (date.today().month, date.today().day)
                < (value.date_of_birth.month, value.date_of_birth.day)
            ),
            height_cm=value.height_cm,
            interests=[InterestResponse(id=i.id, name=i.name) for i in value.interests],
            profile_completion_percentage=value.profile_completion_percentage,
        )


class DiscoveryService:
    def __init__(self, db: AsyncSession, ranking: RankingStrategy | None = None):
        self.db, self.repo, self.ranking = db, DiscoveryRepository(db), ranking or RankingStrategy()

    async def discover(self, user: User, cursor: str | None, limit: int) -> DiscoveryPage:
        own = await self.repo.profile_for_user(user.id)
        if not own or own.profile_completion_percentage < 100:
            raise DiscoveryError("Complete your profile before discovery", 403)
        keyset = decode_cursor(cursor)
        rows = await self.repo.candidates(user.id, [i.id for i in own.interests], keyset, limit)
        has_more = len(rows) > limit
        return DiscoveryPage(
            candidates=[self.ranking.profile(row) for row in rows[:limit]],
            next_cursor=(
                encode_cursor(
                    rows[limit - 1].profile_completion_percentage, rows[limit - 1].username
                )
                if has_more
                else None
            ),
        )

    async def action(self, user: User, target: UUID, model) -> None:
        if target == user.id:
            raise DiscoveryError("You cannot act on your own profile", 422)
        if not await self.repo.target_exists(target):
            raise DiscoveryError("Profile not found", 404)
        await self.repo.record(model, user.id, target)

    async def like(self, user: User, target: UUID) -> None:
        await self.action(user, target, ProfileLike)

    async def pass_profile(self, user: User, target: UUID) -> None:
        await self.action(user, target, ProfilePass)
