from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.discovery.models import ProfileLike, ProfilePass
from app.domain.discovery.repository import DiscoveryRepository, decode_cursor, encode_cursor
from app.domain.discovery.schemas import DiscoveryFilters, DiscoveryPage, DiscoveryProfile
from app.domain.discovery.scoring import RecommendationScorer
from app.domain.identity.models import User
from app.domain.matching.service import MatchService
from app.domain.profile.schemas import InterestResponse
from app.domain.notifications.service import NotificationService
from app.domain.preferences.service import DiscoveryPreferenceService


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
    def __init__(
        self,
        db: AsyncSession,
        ranking: RankingStrategy | None = None,
        scorer: RecommendationScorer | None = None,
    ):
        self.db, self.repo, self.ranking = db, DiscoveryRepository(db), ranking or RankingStrategy()
        self.scorer = scorer or RecommendationScorer()
        self.matching = MatchService(db)
        self.preferences = DiscoveryPreferenceService(db)

    async def discover(
        self,
        user: User,
        cursor: str | None,
        limit: int,
        filters: DiscoveryFilters | None = None,
        has_explicit_filters: bool = False,
    ) -> DiscoveryPage:
        own = await self.repo.profile_for_user(user.id)
        if not own or own.profile_completion_percentage < 100:
            raise DiscoveryError("Complete your profile before discovery", 403)
        filters = filters or DiscoveryFilters()
        if not has_explicit_filters:
            filters = await self.preferences.filters(user.id)
        keyset = decode_cursor(cursor)
        rows = await self.repo.candidates(
            user.id, [i.id for i in own.interests], keyset, limit, filters
        )
        has_more = len(rows) > limit
        return DiscoveryPage(
            candidates=[self.ranking.profile(row) for row, _ in rows[:limit]],
            next_cursor=(
                encode_cursor(
                    rows[limit - 1][1],
                    rows[limit - 1][0].profile_completion_percentage,
                    rows[limit - 1][0].username,
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
        created = await self.repo.record(model, user.id, target, commit=False)
        if model is ProfileLike:
            if created:
                await NotificationService(self.db).create(target, user.id, "LIKE", {})
            match = await self.matching.synchronize_after_like(user.id, target)
            if match:
                await NotificationService(self.db).create(
                    target, user.id, "MATCH", {"match_id": str(match.id)}
                )
                await NotificationService(self.db).create(
                    user.id, target, "MATCH", {"match_id": str(match.id)}
                )
        await self.db.commit()

    async def like(self, user: User, target: UUID) -> None:
        await self.action(user, target, ProfileLike)

    async def pass_profile(self, user: User, target: UUID) -> None:
        await self.action(user, target, ProfilePass)
