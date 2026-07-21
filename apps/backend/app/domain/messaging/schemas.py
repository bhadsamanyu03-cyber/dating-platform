from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class MessageCreate(BaseModel):
    message_type: str = "TEXT"
    text_content: str | None = Field(default=None, max_length=4000)
    media_asset_ids: list[UUID] = Field(default_factory=list, max_length=10)
    client_message_id: UUID

    @model_validator(mode="after")
    def validate_payload(self):
        text = self.text_content.strip() if self.text_content else None
        if not text and not self.media_asset_ids:
            raise ValueError("A message needs text or an attachment")
        if self.message_type not in {"TEXT", "IMAGE", "SYSTEM"}:
            raise ValueError("Unsupported message type")
        if self.message_type == "SYSTEM":
            raise ValueError("System messages cannot be created by users")
        if self.message_type == "IMAGE" and not self.media_asset_ids:
            raise ValueError("Image messages require an asset")
        self.text_content = text
        return self


class MessageResponse(BaseModel):
    id: UUID
    sender_user_id: UUID
    message_type: str
    text_content: str | None
    media_asset_ids: list[UUID] = Field(default_factory=list)
    attachments: list["MessageAttachmentResponse"] = Field(default_factory=list)
    created_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    deleted_at: datetime | None = None
    client_message_id: UUID | None = None


class MessageAttachmentResponse(BaseModel):
    media_id: UUID
    media_type: str
    width: int | None
    height: int | None
    duration_ms: int | None
    thumbnail_url: str | None
    display_url: str
    processing_state: str


class MessagePage(BaseModel):
    messages: list[MessageResponse]
    next_cursor: str | None


class ConversationResponse(BaseModel):
    id: UUID
    match_id: UUID
    created_at: datetime


class ConversationPage(BaseModel):
    conversations: list[ConversationResponse]
    next_cursor: str | None
