import base64
from uuid import UUID
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.discovery.models import ProfileLike, ProfilePass
from app.domain.identity.models import User
from app.domain.profile.models import UserProfile, profile_interests


def decode_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        return int(base64.urlsafe_b64decode(cursor.encode()).decode())
    except Exception as exc:
        raise ValueError("Invalid cursor") from exc


def encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(str(offset).encode()).decode()


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
        self, user_id: UUID, interest_ids: list[UUID], offset: int, limit: int
    ) -> list[UserProfile]:
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
            select(UserProfile)
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
            .offset(offset)
            .limit(limit + 1)
        )
        return list(await self.db.scalars(query))

    async def action_exists(self, model, actor: UUID, target: UUID) -> bool:
        return bool(
            await self.db.scalar(
                select(
                    exists().where(
                        (model.liker_user_id if model is ProfileLike else model.passer_user_id)
                        == actor,
                        (model.liked_user_id if model is ProfileLike else model.passed_user_id)
                        == target,
                    )
                )
            )
        )

    async def record(self, model, actor: UUID, target: UUID) -> None:
        if not await self.action_exists(model, actor, target):
            self.db.add(
                model(
                    **(
                        {"liker_user_id": actor, "liked_user_id": target}
                        if model is ProfileLike
                        else {"passer_user_id": actor, "passed_user_id": target}
                    )
                )
            )
            await self.db.commit()
