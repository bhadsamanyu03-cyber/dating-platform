from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.identity.models import User
from app.domain.presence.schemas import PresenceResponse
from app.domain.presence.service import PresenceService

router = APIRouter(prefix="/presence", tags=["presence"])


@router.get("/{user_id}", response_model=PresenceResponse)
async def presence(
    user_id: UUID,
    _: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> PresenceResponse:
    return await PresenceService(db).get(user_id)
