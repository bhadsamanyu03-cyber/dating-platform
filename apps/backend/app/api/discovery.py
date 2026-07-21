from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.discovery.schemas import DiscoveryAction, DiscoveryFilters, DiscoveryPage
from app.domain.discovery.service import DiscoveryError, DiscoveryService
from app.domain.identity.models import User

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("", response_model=DiscoveryPage)
async def discover(
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    filters: DiscoveryFilters = Depends(),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return await DiscoveryService(db).discover(user, cursor, limit, filters)
    except (DiscoveryError, ValueError) as exc:
        raise HTTPException(
            exc.status_code if isinstance(exc, DiscoveryError) else 422,
            exc.message if isinstance(exc, DiscoveryError) else str(exc),
        ) from exc


@router.post("/like", status_code=204)
async def like(
    payload: DiscoveryAction,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await DiscoveryService(db).like(user, payload.target_user_id)
    except DiscoveryError as exc:
        raise HTTPException(exc.status_code, exc.message) from exc
    return Response(status_code=204)


@router.post("/pass", status_code=204)
async def pass_profile(
    payload: DiscoveryAction,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await DiscoveryService(db).pass_profile(user, payload.target_user_id)
    except DiscoveryError as exc:
        raise HTTPException(exc.status_code, exc.message) from exc
    return Response(status_code=204)
