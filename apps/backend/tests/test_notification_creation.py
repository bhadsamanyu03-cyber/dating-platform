from types import SimpleNamespace
from uuid import uuid4
from datetime import datetime, timezone

import pytest

from app.domain.discovery.models import ProfileLike
from app.domain.discovery.service import DiscoveryService
from app.domain.messaging.schemas import MessageCreate
from app.domain.messaging.service import MessagingService


class Database:
    async def commit(self):
        pass


class DiscoveryRepository:
    async def target_exists(self, _):
        return True

    async def record(self, *_args, **_kwargs):
        return True


class Matching:
    async def synchronize_after_like(self, *_):
        return SimpleNamespace(id=uuid4())


class Notifications:
    created = []

    def __init__(self, _):
        pass

    async def create(self, recipient_id, actor_id, type, payload):
        self.created.append((recipient_id, actor_id, type, payload))


@pytest.mark.asyncio
async def test_like_and_match_notifications_are_created(monkeypatch):
    import app.domain.discovery.service as module

    actor, target = uuid4(), uuid4()
    Notifications.created = []
    monkeypatch.setattr(module, "NotificationService", Notifications)
    service = DiscoveryService(Database())
    service.repo, service.matching = DiscoveryRepository(), Matching()
    await service.action(SimpleNamespace(id=actor), target, ProfileLike)
    assert [(value[0], value[2]) for value in Notifications.created] == [
        (target, "LIKE"),
        (target, "MATCH"),
        (actor, "MATCH"),
    ]


class MessagingRepository:
    async def conversation_for_user(self, *_):
        return SimpleNamespace()

    async def existing_message(self, *_):
        return None

    async def media(self, *_):
        return []

    async def add_message(self, message, _):
        message.id = uuid4()
        message.media = []
        message.created_at = datetime.now(timezone.utc)
        message.delivered_at = None
        message.read_at = None
        message.deleted_at = None
        return message

    async def recipient_for_conversation(self, _, __):
        return uuid4()


@pytest.mark.asyncio
async def test_new_message_notification_is_created(monkeypatch):
    import app.domain.messaging.service as module

    Notifications.created = []
    monkeypatch.setattr(module, "NotificationService", Notifications)
    service = MessagingService(Database())
    service.repo = MessagingRepository()
    await service.send(
        uuid4(), uuid4(), MessageCreate(text_content="Hi", client_message_id=uuid4())
    )
    assert len(Notifications.created) == 1
    assert Notifications.created[0][2] == "MESSAGE"
