from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.engagement.schemas import CommentCreate
from app.domain.engagement.service import EngagementError, EngagementService
from app.domain.feed.schemas import PostCreate
from app.domain.feed.service import FeedError, FeedService


class Database:
    def __init__(self):
        self.commits = 0
        self.added = []

    def add(self, value):
        self.added.append(value)

    async def commit(self):
        self.commits += 1

    async def refresh(self, value):
        if value.created_at is None:
            value.created_at = datetime.now(timezone.utc)


def post(author=None, minutes=0):
    return SimpleNamespace(
        id=uuid4(),
        author_user_id=author or uuid4(),
        caption="Post",
        visibility="PUBLIC",
        created_at=datetime.now(timezone.utc) - timedelta(minutes=minutes),
        deleted_at=None,
    )


class FeedRepository:
    def __init__(self, values=()):
        self.values, self.added = list(values), []

    async def assets(self, ids, _):
        return [SimpleNamespace(id=value) for value in ids]

    async def add(self, value):
        value.id, value.created_at = uuid4(), datetime.now(timezone.utc)
        self.added.append(value)

    async def post(self, post_id, _):
        return next((value for value in self.values if value.id == post_id), None)

    async def media(self, _):
        return []

    async def counts(self, _):
        return 0, 0

    async def list(self, *_):
        return self.values

    async def media_for_posts(self, ids):
        return {post_id: [] for post_id in ids}

    async def counts_for_posts(self, ids):
        return {post_id: (0, 0) for post_id in ids}


@pytest.mark.asyncio
async def test_create_delete_and_paginate_feed_posts():
    user = uuid4()
    db = Database()
    service = FeedService(db)
    service.repo = FeedRepository([post(user, 0), post(user, 1), post(user, 2)])
    created = await service.create(user, PostCreate(caption="Hello"))
    assert created.author_user_id == user
    page = await service.list(user, None, 2)
    assert len(page.posts) == 2 and page.next_cursor
    target = service.repo.values[0]
    await service.delete(target.id, user)
    assert target.deleted_at is not None
    with pytest.raises(FeedError, match="not found"):
        await service.delete(service.repo.values[1].id, uuid4())


class EngagementRepository:
    def __init__(self, target, *, like_created=True, comment=None):
        self.target, self.like_created, self.comment_value = target, like_created, comment

    async def post(self, _):
        return self.target

    async def like(self, *_):
        return self.like_created

    async def unlike(self, *_):
        pass

    async def comment(self, value):
        value.id, value.created_at = uuid4(), datetime.now(timezone.utc)
        self.comment_value = value

    async def comments(self, *_):
        return [self.comment_value] if self.comment_value else []

    async def owned_comment(self, comment_id, user):
        if (
            self.comment_value
            and self.comment_value.id == comment_id
            and self.comment_value.author_user_id == user
        ):
            return self.comment_value
        return None


class Notifications:
    values = []

    def __init__(self, _):
        pass

    async def create(self, recipient, actor, type, payload):
        self.values.append((recipient, actor, type, payload))


@pytest.mark.asyncio
async def test_likes_comments_authorization_and_notifications(monkeypatch):
    import app.domain.engagement.service as module

    author, actor = uuid4(), uuid4()
    target = post(author)
    Notifications.values = []
    monkeypatch.setattr(module, "NotificationService", Notifications)
    service = EngagementService(Database())
    service.repo = EngagementRepository(target)
    await service.like(target.id, actor)
    comment = await service.create_comment(target.id, actor, CommentCreate(body="Nice post"))
    assert [value[2] for value in Notifications.values] == ["POST_LIKE", "POST_COMMENT"]
    await service.delete_comment(comment.id, actor)
    with pytest.raises(EngagementError, match="not found"):
        await service.delete_comment(comment.id, uuid4())
    service.repo.like_created = False
    with pytest.raises(EngagementError, match="already liked"):
        await service.like(target.id, actor)
