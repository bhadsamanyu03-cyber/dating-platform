from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.matching.models import Match
from app.domain.matching.repository import MatchRepository, decode_cursor, encode_cursor
from app.domain.matching.schemas import MatchPage, MatchResponse, MatchSummary
from app.domain.messaging.service import MessagingService


class MatchError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message, self.status_code = message, status_code


class MatchService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, MatchRepository(db)

    async def synchronize_after_like(self, actor: UUID, target: UUID) -> Match | None:
        if actor == target:
            raise MatchError("Users cannot match themselves", 422)
        await self.repo.lock_pair(actor, target)
        if not await self.repo.reciprocal_like_exists(actor, target):
            return None
        match = await self.repo.create_pair(actor, target)
        if match:
            await MessagingService(self.db).ensure_conversation(match.id)
        return match

    async def response(self, match: Match, user_id: UUID) -> MatchResponse:
        profile = await self.repo.other_profile(match, user_id)
        if not profile:
            raise MatchError("Match not found", 404)
        return MatchResponse(
            id=match.id,
            created_at=match.created_at,
            updated_at=match.updated_at,
            match=MatchSummary(
                user_id=profile.user_id,
                username=profile.username,
                display_name=profile.display_name,
            ),
        )

    async def list(self, user_id: UUID, cursor: str | None, limit: int) -> MatchPage:
        rows = await self.repo.list_for_user(user_id, decode_cursor(cursor), limit)
        page = [await self.response(match, user_id) for match in rows[:limit]]
        return MatchPage(
            matches=page,
            next_cursor=(
                encode_cursor(rows[limit - 1].created_at, rows[limit - 1].id)
                if len(rows) > limit
                else None
            ),
        )

    async def get(self, match_id: UUID, user_id: UUID) -> MatchResponse:
        match = await self.repo.get_for_user(match_id, user_id)
        if not match:
            raise MatchError("Match not found", 404)
        return await self.response(match, user_id)

    async def unmatch(self, match_id: UUID, user_id: UUID) -> None:
        match = await self.repo.get_for_user(match_id, user_id)
        if not match:
            raise MatchError("Match not found", 404)
        await self.repo.delete(match)
        await self.db.commit()
