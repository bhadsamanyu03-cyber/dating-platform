from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.identity.models import User
from app.domain.notifications.schemas import NotificationPage, UnreadNotificationCount
from app.domain.notifications.service import NotificationError, NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationPage)
async def notifications(
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> NotificationPage:
    try:
        return await NotificationService(db).list(user.id, cursor, limit)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/unread-count", response_model=UnreadNotificationCount)
async def unread_count(
    user: User = Depends(current_user), db: AsyncSession = Depends(get_database_session)
) -> UnreadNotificationCount:
    return await NotificationService(db).unread_count(user.id)


@router.post("/{notification_id}/read", status_code=204)
async def mark_read(
    notification_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await NotificationService(db).mark_read(notification_id, user.id)
    except NotificationError as exc:
        raise HTTPException(exc.status_code, exc.message) from exc
    return Response(status_code=204)


@router.post("/read-all", status_code=204)
async def mark_all_read(
    user: User = Depends(current_user), db: AsyncSession = Depends(get_database_session)
) -> Response:
    await NotificationService(db).mark_all_read(user.id)
    return Response(status_code=204)
