from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.reports.models import ModerationStatus, Report
from app.domain.reports.repository import ReportRepository, decode_cursor, encode_cursor
from app.domain.reports.schemas import ReportCreate, ReportPage, ReportResponse


class ReportError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message, self.status_code = message, status_code


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, ReportRepository(db)

    @staticmethod
    def response(value: Report) -> ReportResponse:
        return ReportResponse(
            id=value.id,
            reporter_id=value.reporter_id,
            target_user_id=value.target_user_id,
            reason=value.reason,
            description=value.description,
            status=ModerationStatus(value.status),
            created_at=value.created_at,
        )

    async def create(self, reporter_id: UUID, payload: ReportCreate) -> ReportResponse:
        if reporter_id == payload.target_user_id:
            raise ReportError("You cannot report yourself", 422)
        if not await self.repo.target_exists(payload.target_user_id):
            raise ReportError("User not found", 404)
        if await self.repo.active_exists(reporter_id, payload.target_user_id):
            raise ReportError("An active report already exists", 409)
        report = await self.repo.create(
            Report(
                reporter_id=reporter_id,
                target_user_id=payload.target_user_id,
                reason=payload.reason,
                description=payload.description,
                status=ModerationStatus.OPEN.value,
            )
        )
        await self.db.commit()
        return self.response(report)

    async def list(self, reporter_id: UUID, cursor: str | None, limit: int) -> ReportPage:
        values = await self.repo.list_for_reporter(reporter_id, decode_cursor(cursor), limit)
        page = values[:limit]
        return ReportPage(
            reports=[self.response(value) for value in page],
            next_cursor=encode_cursor(page[-1]) if len(values) > limit and page else None,
        )

    async def get(self, report_id: UUID, reporter_id: UUID) -> ReportResponse:
        report = await self.repo.get_for_reporter(report_id, reporter_id)
        if not report:
            raise ReportError("Report not found", 404)
        return self.response(report)
