from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class MediaMetadata(BaseModel):
    id: UUID
    original_filename: str
    mime_type: str
    media_type: str
    file_size_bytes: int
    checksum_sha256: str
    upload_status: str
    created_at: datetime
