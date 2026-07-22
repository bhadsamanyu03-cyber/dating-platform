from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.core.config import get_settings
from app.domain.identity.models import User
from app.domain.media.schemas import MediaMetadata
from app.domain.media.service import MediaError, MediaService
from app.domain.media.storage import storage_provider

router = APIRouter(prefix="/media", tags=["media"])


def service(db: AsyncSession) -> MediaService:
    settings = get_settings()
    return MediaService(
        db,
        storage_provider(settings),
        image_upload_limit=settings.media_image_max_upload_bytes,
        video_upload_limit=settings.media_video_max_upload_bytes,
        upload_chunk_bytes=settings.media_upload_chunk_bytes,
    )


@router.post("/upload", response_model=MediaMetadata, status_code=201)
async def upload(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> MediaMetadata:
    try:
        return service(db).metadata(await service(db).upload(user.id, file))
    except MediaError as error:
        raise HTTPException(error.status_code, error.message) from error


@router.get("/{asset_id}/metadata", response_model=MediaMetadata)
async def metadata(
    asset_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> MediaMetadata:
    try:
        return service(db).metadata(await service(db).get(asset_id, user.id))
    except MediaError as error:
        raise HTTPException(error.status_code, error.message) from error


@router.get("/{asset_id}")
async def download(
    asset_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> StreamingResponse:
    try:
        media_service = service(db)
        asset = await media_service.get(asset_id, user.id)
        return StreamingResponse(
            media_service.storage.download(asset.storage_key),
            media_type=asset.mime_type,
            headers={"Content-Disposition": f'attachment; filename="{asset.original_filename}"'},
        )
    except MediaError as error:
        raise HTTPException(error.status_code, error.message) from error


@router.delete("/{asset_id}", status_code=204)
async def delete(
    asset_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await service(db).delete(asset_id, user.id)
    except MediaError as error:
        raise HTTPException(error.status_code, error.message) from error
    return Response(status_code=204)
