import base64
from uuid import UUID
from sqlalchemy import exists, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.discovery.models import ProfileLike, ProfilePass
from app.domain.identity.models import User
from app.domain.profile.models import UserProfile, profile_interests


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
        query = (
            select(UserProfile, shared.label("shared_count"))
            .where(
                UserProfile.user_id != user_id,
                exists().where(
                    User.id == UserProfile.user_id,
                    User.is_active.is_(True),
                    User.deleted_at.is_(None),
                ),
                ~liked,
                ~passed,
            )
            .order_by(
                shared.desc(),
                UserProfile.profile_completion_percentage.desc(),
                UserProfile.username,
            )
            .limit(limit + 1)
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

    async def record(self, model, actor: UUID, target: UUID) -> None:
        values = (
            {"liker_user_id": actor, "liked_user_id": target}
            if model is ProfileLike
            else {"passer_user_id": actor, "passed_user_id": target}
        )
        await self.db.execute(insert(model).values(**values).on_conflict_do_nothing())
        await self.db.commit()
