from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class PostCreate(BaseModel):
    caption: str | None = Field(default=None, max_length=500)
    visibility: str = "PUBLIC"
    media_asset_ids: list[UUID] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def validate_post(self):
        if self.visibility not in {"PUBLIC", "PRIVATE"}:
            raise ValueError("Unsupported visibility")
        if len(set(self.media_asset_ids)) != len(self.media_asset_ids):
            raise ValueError("Duplicate media references")
        if not self.caption and not self.media_asset_ids:
            raise ValueError("Post content is required")
        return self


class PostResponse(BaseModel):
    id: UUID
    author_user_id: UUID
    caption: str | None
    visibility: str
    media_asset_ids: list[UUID]
    created_at: datetime


class PostPage(BaseModel):
    posts: list[PostResponse]
    next_cursor: str | None
