from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.identity.models import User
from app.domain.profile.repository import ProfileRepository
from app.domain.profile.schemas import (
    InterestResponse,
    ProfileResponse,
    ProfileUpdate,
    UsernameAvailability,
)
from app.domain.profile.service import ProfileError, ProfileService

profile_router = APIRouter(prefix="/profile", tags=["profile"])
interests_router = APIRouter(prefix="/interests", tags=["interests"])


def output(profile) -> ProfileResponse:
    return ProfileResponse(
        username=profile.username,
        display_name=profile.display_name,
        bio=profile.bio,
        gender=profile.gender,
        pronouns=profile.pronouns,
        date_of_birth=profile.date_of_birth,
        height_cm=profile.height_cm,
        interests=[InterestResponse(id=i.id, name=i.name) for i in profile.interests],
        profile_photo_count=profile.profile_photo_count,
        profile_video_count=profile.profile_video_count,
        profile_completion_percentage=profile.profile_completion_percentage,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@profile_router.get("/me", response_model=ProfileResponse)
async def me(user: User = Depends(current_user), db: AsyncSession = Depends(get_database_session)):
    profile = await ProfileRepository(db).by_user(user.id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return output(profile)


@profile_router.put("/me", response_model=ProfileResponse)
async def update(
    payload: ProfileUpdate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return output(await ProfileService(db).update(user, payload))
    except ProfileError as exc:
        raise HTTPException(exc.status_code, exc.message) from exc


@profile_router.get("/check-username", response_model=UsernameAvailability)
async def check_username(username: str, db: AsyncSession = Depends(get_database_session)):
    from app.domain.profile.schemas import USERNAME

    if not USERNAME.fullmatch(username):
        raise HTTPException(422, "Invalid username")
    return UsernameAvailability(
        username=username, available=await ProfileRepository(db).by_username(username) is None
    )


@profile_router.get("/{username}", response_model=ProfileResponse)
async def public(username: str, db: AsyncSession = Depends(get_database_session)):
    profile = await ProfileRepository(db).by_username(username)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return output(profile)


@interests_router.get("", response_model=list[InterestResponse])
async def interests(db: AsyncSession = Depends(get_database_session)):
    return [InterestResponse(id=i.id, name=i.name) for i in await ProfileRepository(db).interests()]
