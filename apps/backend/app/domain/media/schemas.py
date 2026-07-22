from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MediaMetadata(BaseModel):
    id: UUID
    original_filename: str
    mime_type: str
    media_type: str
    file_size_bytes: int
    checksum_sha256: str
    upload_status: str
    processing_state: str
    width: int | None
    height: int | None
    duration_ms: int | None
    aspect_ratio: str | None
    orientation: int | None
    codec: str | None
    created_at: datetime


class PresignedUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str


class PresignedUrlResponse(BaseModel):
    url: str
    method: str
    storage_key: str
    expires_in: int
