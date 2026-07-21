from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.identity.models import User
from app.domain.profile.repository import ProfileRepository
from app.domain.profile.schemas import (
    InterestResponse,
    ProfileResponse,
    ProfileUpdate,
    UsernameAvailability,
    ProfilePhotoCreate,
    ProfilePhotoResponse,
)
from app.domain.profile.service import ProfileError, ProfileService
from app.core.config import get_settings
from app.domain.media.storage import LocalStorageProvider

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


def photo_output(photo) -> ProfilePhotoResponse:
    return ProfilePhotoResponse(
        id=photo.id,
        media_asset_id=photo.media_asset_id,
        ordering=photo.ordering,
        created_at=photo.created_at,
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


@profile_router.post("/me/photos", response_model=ProfilePhotoResponse, status_code=201)
async def add_photo(
    payload: ProfilePhotoCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> ProfilePhotoResponse:
    try:
        return photo_output(await ProfileService(db).add_photo(user, payload.media_asset_id, payload.ordering))
    except ProfileError as exc:
        raise HTTPException(exc.status_code, exc.message) from exc


@profile_router.get("/{username}/photos", response_model=list[ProfilePhotoResponse])
async def photos(
    username: str,
    _: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> list[ProfilePhotoResponse]:
    profile = await ProfileRepository(db).by_username(username)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return [photo_output(photo) for photo in await ProfileRepository(db).photos(profile.id)]


@profile_router.get("/{username}/photos/{photo_id}")
async def download_photo(
    username: str,
    photo_id: UUID,
    _: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> StreamingResponse:
    repository = ProfileRepository(db)
    profile = await repository.by_username(username)
    if not profile:
        raise HTTPException(404, "Profile not found")
    photo = await repository.photo(profile.id, photo_id)
    if not photo:
        raise HTTPException(404, "Profile photo not found")
    asset = await repository.owned_image_asset(photo.media_asset_id, profile.user_id)
    if not asset:
        raise HTTPException(404, "Profile photo not found")
    return StreamingResponse(
        LocalStorageProvider(get_settings().media_storage_path).download(asset.storage_key),
        media_type=asset.mime_type,
    )


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
