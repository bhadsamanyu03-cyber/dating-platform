from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PresenceResponse(BaseModel):
    user_id: UUID
    status: str
    last_seen_at: datetime | None
