from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.messaging.schemas import MessageCreate
from app.domain.messaging.service import decode_cursor


def test_message_requires_content() -> None:
    with pytest.raises(ValidationError):
        MessageCreate(client_message_id=uuid4())


def test_message_accepts_mixed_text_and_images() -> None:
    payload = MessageCreate(text_content="Hello", media_asset_ids=[uuid4(), uuid4()], client_message_id=uuid4())
    assert payload.text_content == "Hello" and len(payload.media_asset_ids) == 2


def test_invalid_cursor_is_rejected() -> None:
    with pytest.raises(Exception, match="Invalid cursor"):
        decode_cursor("not-a-cursor")
