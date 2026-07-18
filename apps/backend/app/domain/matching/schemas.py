from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MatchSummary(BaseModel):
    user_id: UUID
    username: str
    display_name: str


class MatchResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    match: MatchSummary


class MatchPage(BaseModel):
    matches: list[MatchResponse]
    next_cursor: str | None
