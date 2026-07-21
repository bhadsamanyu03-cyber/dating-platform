from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.reports.models import ModerationStatus


class ReportCreate(BaseModel):
    target_user_id: UUID
    reason: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)


class ReportResponse(BaseModel):
    id: UUID
    reporter_id: UUID
    target_user_id: UUID
    reason: str
    description: str | None
    status: ModerationStatus
    created_at: datetime


class ReportPage(BaseModel):
    reports: list[ReportResponse]
    next_cursor: str | None
