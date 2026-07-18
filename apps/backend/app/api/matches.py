from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.identity.models import User
from app.domain.matching.schemas import MatchPage, MatchResponse
from app.domain.matching.service import MatchError, MatchService

router = APIRouter(prefix="/matches", tags=["matches"])


def matching_error(error: MatchError) -> HTTPException:
    return HTTPException(error.status_code, error.message)


@router.get("", response_model=MatchPage)
async def list_matches(
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> MatchPage:
    try:
        return await MatchService(db).list(user.id, cursor, limit)
    except (MatchError, ValueError) as error:
        raise (
            matching_error(error)
            if isinstance(error, MatchError)
            else HTTPException(422, str(error))
        ) from error


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> MatchResponse:
    try:
        return await MatchService(db).get(match_id, user.id)
    except MatchError as error:
        raise matching_error(error) from error


@router.delete("/{match_id}", status_code=204)
async def unmatch(
    match_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await MatchService(db).unmatch(match_id, user.id)
    except MatchError as error:
        raise matching_error(error) from error
    return Response(status_code=204)
