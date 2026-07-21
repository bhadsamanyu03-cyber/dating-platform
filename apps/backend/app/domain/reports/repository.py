import base64
import binascii
import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.reports.models import ModerationStatus, Report


def encode_cursor(report: Report) -> str:
    return base64.urlsafe_b64encode(
        json.dumps([report.created_at.isoformat(), str(report.id)]).encode()
    ).decode()


def decode_cursor(cursor: str | None) -> tuple[datetime, UUID] | None:
    if not cursor:
        return None
    try:
        created_at, report_id = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return datetime.fromisoformat(created_at), UUID(report_id)
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError):
        raise ValueError("Invalid cursor") from None


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def target_exists(self, user_id: UUID) -> bool:
        from app.domain.identity.models import User

        return bool(await self.db.scalar(select(User.id).where(User.id == user_id)))

    async def active_exists(self, reporter_id: UUID, target_user_id: UUID) -> bool:
        return bool(
            await self.db.scalar(
                select(Report.id).where(
                    Report.reporter_id == reporter_id,
                    Report.target_user_id == target_user_id,
                    Report.status.in_(
                        [ModerationStatus.OPEN.value, ModerationStatus.UNDER_REVIEW.value]
                    ),
                )
            )
        )

    async def create(self, report: Report) -> Report:
        self.db.add(report)
        await self.db.flush()
        return report

    async def list_for_reporter(
        self, reporter_id: UUID, cursor: tuple[datetime, UUID] | None, limit: int
    ) -> list[Report]:
        query = select(Report).where(Report.reporter_id == reporter_id)
        if cursor:
            created_at, report_id = cursor
            query = query.where(
                or_(
                    Report.created_at < created_at,
                    and_(Report.created_at == created_at, Report.id < report_id),
                )
            )
        return list(
            (
                await self.db.scalars(
                    query.order_by(Report.created_at.desc(), Report.id.desc()).limit(limit + 1)
                )
            ).all()
        )

    async def get_for_reporter(self, report_id: UUID, reporter_id: UUID) -> Report | None:
        return await self.db.scalar(
            select(Report).where(Report.id == report_id, Report.reporter_id == reporter_id)
        )
