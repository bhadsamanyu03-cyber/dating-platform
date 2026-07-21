from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.identity.models import User
from app.domain.reports.schemas import ReportCreate, ReportPage, ReportResponse
from app.domain.reports.service import ReportError, ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=201)
async def create_report(
    payload: ReportCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> ReportResponse:
    try:
        return await ReportService(db).create(user.id, payload)
    except ReportError as exc:
        raise HTTPException(exc.status_code, exc.message) from exc


@router.get("/me", response_model=ReportPage)
async def reports(
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> ReportPage:
    try:
        return await ReportService(db).list(user.id, cursor, limit)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/{report_id}", response_model=ReportResponse)
async def report(
    report_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> ReportResponse:
    try:
        return await ReportService(db).get(report_id, user.id)
    except ReportError as exc:
        raise HTTPException(exc.status_code, exc.message) from exc
