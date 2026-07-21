import base64
from uuid import UUID
from sqlalchemy import and_, exists, func, or_, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.discovery.models import ProfileBlock, ProfileLike, ProfilePass
from app.domain.identity.models import User
from app.domain.matching.models import Match
from app.domain.profile.models import UserProfile, profile_interests
from app.domain.discovery.schemas import DiscoveryFilters


def decode_cursor(cursor: str | None) -> tuple[int, int, str] | None:
    if not cursor:
        return None
    try:
        shared_count, completion, username = (
            base64.urlsafe_b64decode(cursor.encode()).decode().split(":", 2)
        )
        return int(shared_count), int(completion), username
    except Exception as exc:
        raise ValueError("Invalid cursor") from exc


def encode_cursor(shared_count: int, completion: int, username: str) -> str:
    return base64.urlsafe_b64encode(f"{shared_count}:{completion}:{username}".encode()).decode()


class DiscoveryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def profile_for_user(self, user_id: UUID) -> UserProfile | None:
        return await self.db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))

    async def target_exists(self, user_id: UUID) -> bool:
        return bool(
            await self.db.scalar(
                select(
                    exists().where(
                        User.id == user_id, User.is_active.is_(True), User.deleted_at.is_(None)
                    )
                )
            )
        )

    async def candidates(
        self,
        user_id: UUID,
        interest_ids: list[UUID],
        cursor: tuple[int, int, str] | None,
        limit: int,
        filters: DiscoveryFilters,
    ) -> list[tuple[UserProfile, int]]:
        shared = (
            select(func.count())
            .select_from(profile_interests)
            .where(
                profile_interests.c.profile_id == UserProfile.id,
                profile_interests.c.interest_id.in_(interest_ids or [UUID(int=0)]),
            )
            .scalar_subquery()
        )
        liked = exists().where(
            ProfileLike.liker_user_id == user_id, ProfileLike.liked_user_id == UserProfile.user_id
        )
        passed = exists().where(
            ProfilePass.passer_user_id == user_id, ProfilePass.passed_user_id == UserProfile.user_id
        )
        blocked = exists().where(
            or_(
                and_(
                    ProfileBlock.blocker_user_id == user_id,
                    ProfileBlock.blocked_user_id == UserProfile.user_id,
                ),
                and_(
                    ProfileBlock.blocker_user_id == UserProfile.user_id,
                    ProfileBlock.blocked_user_id == user_id,
                ),
            )
        )
        matched = exists().where(
            or_(
                and_(Match.user_one_id == user_id, Match.user_two_id == UserProfile.user_id),
                and_(Match.user_two_id == user_id, Match.user_one_id == UserProfile.user_id),
            )
        )
        age = func.extract("year", func.age(func.current_date(), UserProfile.date_of_birth))
        query = (
            select(UserProfile, shared.label("shared_count"))
            .where(
                UserProfile.user_id != user_id,
                UserProfile.is_discoverable.is_(True),
                UserProfile.profile_completion_percentage >= filters.minimum_profile_completion,
                exists().where(
                    User.id == UserProfile.user_id,
                    User.is_active.is_(True),
                    User.deleted_at.is_(None),
                ),
                ~liked,
                ~passed,
                ~blocked,
                ~matched,
            )
            .order_by(
                shared.desc(),
                UserProfile.profile_completion_percentage.desc(),
                UserProfile.username,
            )
            .limit(limit + 1)
        )
        if filters.gender:
            query = query.where(UserProfile.gender == filters.gender)
        if filters.min_age is not None:
            query = query.where(age >= filters.min_age)
        if filters.max_age is not None:
            query = query.where(age <= filters.max_age)
        if filters.verified_only:
            query = query.where(
                exists().where(User.id == UserProfile.user_id, User.is_email_verified.is_(True))
            )
        if filters.active_recently:
            query = query.where(
                exists().where(
                    User.id == UserProfile.user_id,
                    User.updated_at >= func.now() - text("interval '30 days'"),
                )
            )
        if cursor:
            shared_count, completion, username = cursor
            query = query.where(
                (shared < shared_count)
                | (
                    (shared == shared_count)
                    & (UserProfile.profile_completion_percentage < completion)
                )
                | (
                    (shared == shared_count)
                    & (UserProfile.profile_completion_percentage == completion)
                    & (UserProfile.username > username)
                )
            )
        return [(row[0], row[1]) for row in (await self.db.execute(query)).all()]

    async def record(self, model, actor: UUID, target: UUID, commit: bool = True) -> None:
        values = (
            {"liker_user_id": actor, "liked_user_id": target}
            if model is ProfileLike
            else {"passer_user_id": actor, "passed_user_id": target}
        )
        await self.db.execute(insert(model).values(**values).on_conflict_do_nothing())
        if commit:
            await self.db.commit()
