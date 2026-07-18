from uuid import uuid4

import pytest

from app.domain.matching.service import MatchError, MatchService


class Repository:
    def __init__(self, reciprocal=True):
        self.reciprocal, self.created = reciprocal, []

    async def reciprocal_like_exists(self, *_):
        return self.reciprocal

    async def lock_pair(self, *_):
        return None

    async def create_pair(self, first, second):
        self.created.append((first, second))
        return None


@pytest.mark.asyncio
async def test_mutual_like_is_idempotent_and_self_match_is_rejected():
    first, second = uuid4(), uuid4()
    service = MatchService(None)
    service.repo = Repository()
    assert await service.synchronize_after_like(first, second) is None
    assert service.repo.created == [(first, second)]
    with pytest.raises(MatchError, match="themselves"):
        await service.synchronize_after_like(first, first)


@pytest.mark.asyncio
async def test_non_mutual_like_does_not_create_a_match():
    service = MatchService(None)
    service.repo = Repository(reciprocal=False)
    assert await service.synchronize_after_like(uuid4(), uuid4()) is None
    assert service.repo.created == []
