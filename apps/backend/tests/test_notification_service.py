from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.notifications.repository import decode_cursor, encode_cursor
from app.domain.notifications.service import NotificationError, NotificationService


class Repository:
    def __init__(self, values=()):
        self.values, self.read, self.all_read = list(values), set(), False

    async def list_for_recipient(self, *_):
        return self.values

    async def unread_count(self, _):
        return 2

    async def mark_read(self, notification_id, _):
        if notification_id not in {value.id for value in self.values}:
            return False
        self.read.add(notification_id)
        return True

    async def mark_all_read(self, _):
        self.all_read = True


class Database:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


def notification(minutes=0):
    return SimpleNamespace(
        id=uuid4(),
        recipient_id=uuid4(),
        actor_id=None,
        type="LIKE",
        payload={},
        is_read=False,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=minutes),
    )


def service(values=()):
    db = Database()
    subject = NotificationService(db)
    subject.repo = Repository(values)
    return subject, db


@pytest.mark.asyncio
async def test_unread_count_and_marking_notifications_read():
    first = notification()
    subject, db = service([first])
    assert (await subject.unread_count(first.recipient_id)).count == 2
    await subject.mark_read(first.id, first.recipient_id)
    await subject.mark_all_read(first.recipient_id)
    assert subject.repo.read == {first.id} and subject.repo.all_read and db.commits == 2
    with pytest.raises(NotificationError, match="not found"):
        await subject.mark_read(uuid4(), first.recipient_id)


@pytest.mark.asyncio
async def test_notification_keyset_pagination_and_cursor():
    values = [notification(0), notification(1), notification(2)]
    subject, _ = service(values)
    page = await subject.list(values[0].recipient_id, None, 2)
    assert [value.id for value in page.notifications] == [values[0].id, values[1].id]
    assert page.next_cursor
    assert decode_cursor(page.next_cursor) == (values[1].created_at, values[1].id)
    assert encode_cursor(values[1]) == page.next_cursor


def test_invalid_notification_cursor_is_rejected():
    with pytest.raises(ValueError, match="Invalid cursor"):
        decode_cursor("invalid")
