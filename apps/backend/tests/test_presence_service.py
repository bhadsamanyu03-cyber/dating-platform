from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.presence.service import PresenceService, TypingService


class Database:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


class Repository:
    def __init__(self, value=None):
        self.value = value

    async def get(self, _):
        return self.value

    async def create(self, value):
        self.value = value
        return value


def service(value=None):
    subject = PresenceService(
        Database(), SimpleNamespace(presence_away_seconds=60, presence_offline_seconds=120)
    )
    subject.repo = Repository(value)
    return subject


@pytest.mark.asyncio
async def test_presence_touch_and_away_offline_transitions():
    user = uuid4()
    subject = service()
    await subject.touch(user)
    assert subject.repo.value.status == "online"
    now = datetime.now(UTC)
    subject.repo.value.last_seen_at = now - timedelta(seconds=61)
    assert (await subject.get(user)).status == "away"
    subject.repo.value.last_seen_at = now - timedelta(seconds=121)
    assert (await subject.get(user)).status == "offline"


class Redis:
    def __init__(self):
        self.values = {}

    async def set(self, key, value, ex):
        self.values[key] = (value, ex)

    async def delete(self, key):
        self.values.pop(key, None)


@pytest.mark.asyncio
async def test_typing_start_stop_and_redis_failure_degrade_gracefully():
    settings = SimpleNamespace(typing_ttl_seconds=8)
    redis = Redis()
    service = TypingService(redis, settings)
    conversation, user = uuid4(), uuid4()
    await service.start(conversation, user)
    assert redis.values[service.key(conversation, user)][1] == 8
    await service.stop(conversation, user)
    assert not redis.values

    class BrokenRedis:
        async def set(self, *_args, **_kwargs):
            raise RuntimeError("unavailable")

        async def delete(self, *_args, **_kwargs):
            raise RuntimeError("unavailable")

    broken = TypingService(BrokenRedis(), settings)
    await broken.start(conversation, user)
    await broken.stop(conversation, user)
