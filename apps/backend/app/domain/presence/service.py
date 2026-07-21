from datetime import UTC, datetime, timedelta
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.domain.presence.models import UserPresence
from app.domain.presence.repository import PresenceRepository
from app.domain.presence.schemas import PresenceResponse


class PresenceService:
    def __init__(self, db: AsyncSession, settings: Settings | None = None):
        self.db, self.repo, self.settings = db, PresenceRepository(db), settings or get_settings()

    def status(self, last_seen_at: datetime, now: datetime | None = None) -> str:
        now = now or datetime.now(UTC)
        elapsed = now - last_seen_at
        if elapsed >= timedelta(seconds=self.settings.presence_offline_seconds):
            return "offline"
        if elapsed >= timedelta(seconds=self.settings.presence_away_seconds):
            return "away"
        return "online"

    async def touch(self, user_id: UUID) -> None:
        value = await self.repo.get(user_id)
        now = datetime.now(UTC)
        if value is None:
            await self.repo.create(UserPresence(user_id=user_id, last_seen_at=now, status="online"))
        else:
            value.last_seen_at, value.status = now, "online"
        await self.db.commit()

    async def get(self, user_id: UUID) -> PresenceResponse:
        value = await self.repo.get(user_id)
        if value is None:
            return PresenceResponse(user_id=user_id, status="offline", last_seen_at=None)
        status = self.status(value.last_seen_at)
        if status != value.status:
            value.status = status
            await self.db.commit()
        return PresenceResponse(user_id=user_id, status=status, last_seen_at=value.last_seen_at)


class TypingService:
    def __init__(self, redis: Redis, settings: Settings | None = None):
        self.redis, self.settings = redis, settings or get_settings()

    @staticmethod
    def key(conversation_id: UUID, user_id: UUID) -> str:
        return f"typing:{conversation_id}:{user_id}"

    async def start(self, conversation_id: UUID, user_id: UUID) -> None:
        try:
            await self.redis.set(
                self.key(conversation_id, user_id), "1", ex=self.settings.typing_ttl_seconds
            )
        except Exception:
            return None

    async def stop(self, conversation_id: UUID, user_id: UUID) -> None:
        try:
            await self.redis.delete(self.key(conversation_id, user_id))
        except Exception:
            return None
