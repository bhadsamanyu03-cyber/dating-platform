from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.messaging.schemas import MessageCreate
from app.domain.messaging.service import MessagingError, MessagingService


def attachment(kind):
    return SimpleNamespace(kind=kind)


def message_with_attachments():
    image_id, video_id = uuid4(), uuid4()
    image = SimpleNamespace(
        id=image_id,
        media_type="IMAGE",
        width=1600,
        height=900,
        duration_ms=None,
        processing_state="READY",
        variants=[attachment("DISPLAY"), attachment("THUMBNAIL")],
    )
    video = SimpleNamespace(
        id=video_id,
        media_type="VIDEO",
        width=1920,
        height=1080,
        duration_ms=5000,
        processing_state="READY",
        variants=[],
    )
    return SimpleNamespace(
        id=uuid4(),
        sender_user_id=uuid4(),
        message_type="IMAGE",
        text_content=None,
        media=[
            SimpleNamespace(media_asset_id=video_id, ordering=1, media_asset=video),
            SimpleNamespace(media_asset_id=image_id, ordering=0, media_asset=image),
        ],
        created_at=datetime.now(timezone.utc),
        delivered_at=None,
        read_at=None,
        deleted_at=None,
        client_message_id=uuid4(),
    )


def test_message_response_preserves_attachment_order_and_variant_metadata():
    value = message_with_attachments()
    response = MessagingService(None).message_response(value)
    assert response.media_asset_ids == [
        value.media[1].media_asset_id,
        value.media[0].media_asset_id,
    ]
    assert [item.media_type for item in response.attachments] == ["IMAGE", "VIDEO"]
    assert response.attachments[0].thumbnail_url and response.attachments[1].duration_ms == 5000


def test_text_only_and_attachment_only_messages_remain_valid():
    assert MessageCreate(text_content="Hello", client_message_id=uuid4()).media_asset_ids == []
    assert MessageCreate(media_asset_ids=[uuid4()], client_message_id=uuid4()).text_content is None


class Repository:
    async def existing_message(self, *_):
        return None

    async def media(self, *_):
        return []


async def conversation(*_):
    return None


@pytest.mark.asyncio
async def test_unprocessed_deleted_or_unowned_attachments_are_rejected():
    service = MessagingService(None)
    service.repo = Repository()
    service.conversation = conversation
    with pytest.raises(MessagingError, match="Invalid media asset"):
        await service.send(
            uuid4(), uuid4(), MessageCreate(media_asset_ids=[uuid4()], client_message_id=uuid4())
        )
