import base64
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.discovery.models import ProfileLike
from app.domain.matching.models import Match
from app.domain.profile.models import UserProfile


def canonical_pair(first: UUID, second: UUID) -> tuple[UUID, UUID]:
    return (first, second) if first.bytes < second.bytes else (second, first)


def encode_cursor(created_at: datetime, match_id: UUID) -> str:
    return base64.urlsafe_b64encode(f"{created_at.isoformat()}|{match_id}".encode()).decode()


def decode_cursor(cursor: str | None) -> tuple[datetime, UUID] | None:
    if not cursor:
        return None
    try:
        created_at, match_id = base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
        return datetime.fromisoformat(created_at), UUID(match_id)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid cursor") from exc


class MatchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def reciprocal_like_exists(self, actor: UUID, target: UUID) -> bool:
        return bool(
            await self.db.scalar(
                select(ProfileLike.id).where(
                    ProfileLike.liker_user_id == target, ProfileLike.liked_user_id == actor
                )
            )
        )

    async def lock_pair(self, first: UUID, second: UUID) -> None:
        user_one_id, user_two_id = canonical_pair(first, second)
        await self.db.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:pair, 0))"),
            {"pair": f"{user_one_id}:{user_two_id}"},
        )

    async def create_pair(self, first: UUID, second: UUID) -> Match | None:
        user_one_id, user_two_id = canonical_pair(first, second)
        statement = (
            insert(Match)
            .values(user_one_id=user_one_id, user_two_id=user_two_id)
            .on_conflict_do_nothing(index_elements=["user_one_id", "user_two_id"])
            .returning(Match)
        )
        return (await self.db.execute(statement)).scalar_one_or_none()

    async def get_for_user(self, match_id: UUID, user_id: UUID) -> Match | None:
        return await self.db.scalar(
            select(Match).where(
                Match.id == match_id,
                or_(Match.user_one_id == user_id, Match.user_two_id == user_id),
            )
        )

    async def list_for_user(self, user_id: UUID, cursor: tuple[datetime, UUID] | None, limit: int):
        query = select(Match).where(or_(Match.user_one_id == user_id, Match.user_two_id == user_id))
        if cursor:
            created_at, match_id = cursor
            query = query.where(
                or_(
                    Match.created_at < created_at,
                    and_(Match.created_at == created_at, Match.id < match_id),
                )
            )
        return list(
            (
                await self.db.scalars(
                    query.order_by(Match.created_at.desc(), Match.id.desc()).limit(limit + 1)
                )
            ).all()
        )

    async def other_profile(self, match: Match, user_id: UUID) -> UserProfile | None:
        other_id = match.user_two_id if match.user_one_id == user_id else match.user_one_id
        return await self.db.scalar(select(UserProfile).where(UserProfile.user_id == other_id))

    async def delete(self, match: Match) -> None:
        await self.db.delete(match)
