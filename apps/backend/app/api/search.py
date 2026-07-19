from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.discovery.schemas import DiscoveryProfile
from app.domain.search.schemas import ProfileFilters
from app.domain.search.service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/users", response_model=list[DiscoveryProfile])
async def users(
    query: str = Query(min_length=1, max_length=100),
    gender: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    verified_only: bool = False,
    profile_complete_only: bool = False,
    limit: int = Query(20, ge=1, le=50),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    return await SearchService(db).users(
        query,
        ProfileFilters(
            gender=gender,
            age_min=age_min,
            age_max=age_max,
            verified_only=verified_only,
            profile_complete_only=profile_complete_only,
        ),
        limit,
    )
