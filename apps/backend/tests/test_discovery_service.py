from datetime import date
from types import SimpleNamespace
from uuid import uuid4
import pytest
from app.domain.discovery.models import ProfileLike
from app.domain.discovery.service import DiscoveryError, DiscoveryService, RankingStrategy
from app.domain.identity.models import User


def profile(user_id=None, username="candidate", completion=100, interests=()):
    return SimpleNamespace(
        user_id=user_id or uuid4(),
        username=username,
        display_name="Candidate",
        bio="",
        gender="Woman",
        pronouns=None,
        date_of_birth=date(2000, 1, 1),
        height_cm=None,
        interests=list(interests),
        profile_completion_percentage=completion,
    )


class Repository:
    def __init__(self, own, rows=()):
        self.own, self.rows, self.recorded = own, list(rows), []

    async def profile_for_user(self, _):
        return self.own

    async def candidates(self, *_):
        return [(row, 0) for row in self.rows]

    async def target_exists(self, _):
        return True

    async def record(self, model, actor, target):
        self.recorded.append((model, actor, target))


def service(own, rows=()):
    result = DiscoveryService(None)
    result.repo = Repository(own, rows)
    return result


@pytest.mark.asyncio
async def test_empty_stack_and_incomplete_profile_gate() -> None:
    user = User(id=uuid4(), email="a@example.com", password_hash="x")
    page = await service(profile(user.id), ()).discover(user, None, 20)
    assert page.candidates == [] and page.next_cursor is None
    with pytest.raises(DiscoveryError, match="Complete"):
        await service(profile(user.id, completion=83)).discover(user, None, 20)


@pytest.mark.asyncio
async def test_pagination_and_duplicate_action_delegation() -> None:
    user = User(id=uuid4(), email="a@example.com", password_hash="x")
    rows = [profile(username="a"), profile(username="b"), profile(username="c")]
    target = rows[0].user_id
    subject = service(profile(user.id), rows)
    page = await subject.discover(user, None, 2)
    assert [candidate.username for candidate in page.candidates] == ["a", "b"]
    assert page.next_cursor
    await subject.like(user, target)
    await subject.like(user, target)
    assert len(subject.repo.recorded) == 2
    assert all(entry[0] is ProfileLike for entry in subject.repo.recorded)


def test_ranking_exposes_age_not_birth_date() -> None:
    candidate = RankingStrategy().profile(profile())
    assert candidate.age >= 18
    assert "date_of_birth" not in candidate.model_dump()
