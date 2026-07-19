"""Stable internal events that future moderation and realtime consumers can subscribe to."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class MessageImageUploaded:
    message_id: UUID
    event_type: str = "message.image_uploaded"
