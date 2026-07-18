from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, model_validator


class MessageCreate(BaseModel):
    message_type: str
    text_content: str | None = None
    media_asset_id: UUID | None = None

    @model_validator(mode="after")
    def validate_payload(self):
        if self.message_type == "TEXT" and (not self.text_content or self.media_asset_id):
            raise ValueError("Text messages require text only")
        if self.message_type in {"IMAGE", "VIDEO"} and not self.media_asset_id:
            raise ValueError("Media messages require an asset")
        if self.message_type not in {"TEXT", "IMAGE", "VIDEO"}:
            raise ValueError("Unsupported message type")
        return self


class MessageResponse(BaseModel):
    id: UUID
    sender_user_id: UUID
    message_type: str
    text_content: str | None
    media_asset_id: UUID | None
    created_at: datetime


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
