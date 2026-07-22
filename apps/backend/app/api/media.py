from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.core.config import get_settings
from app.domain.identity.models import User
from app.domain.media.schemas import MediaMetadata, PresignedUploadRequest, PresignedUrlResponse
from app.domain.media.service import SUPPORTED, MediaError, MediaService
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


@router.post("/presigned-upload", response_model=PresignedUrlResponse)
async def presigned_upload(
    payload: PresignedUploadRequest,
    user: User = Depends(current_user),
) -> PresignedUrlResponse:
    if payload.mime_type not in SUPPORTED:
        raise HTTPException(422, "Unsupported media type")
    settings = get_settings()
    storage = storage_provider(settings)
    if not storage.supports_signed_urls():
        raise HTTPException(400, "Configured storage provider does not support presigned URLs")
    storage_key = f"{user.id}/{uuid4().hex}"
    url = await storage.signed_upload_url(
        storage_key, payload.mime_type, settings.media_signed_url_expiry_seconds
    )
    if not url:
        raise HTTPException(400, "Configured storage provider does not support presigned URLs")
    return PresignedUrlResponse(
        url=url,
        method="PUT",
        storage_key=storage_key,
        expires_in=settings.media_signed_url_expiry_seconds,
    )


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


@router.get("/{asset_id}/presigned-download", response_model=PresignedUrlResponse)
async def presigned_download(
    asset_id: UUID,
    expires_in: int | None = Query(default=None, ge=60, le=86400),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> PresignedUrlResponse:
    try:
        settings = get_settings()
        media_service = service(db)
        asset = await media_service.get(asset_id, user.id)
        if not media_service.storage.supports_signed_urls():
            raise HTTPException(400, "Configured storage provider does not support presigned URLs")
        ttl = expires_in or settings.media_signed_url_expiry_seconds
        url = await media_service.storage.signed_download_url(asset.storage_key, ttl)
        if not url:
            raise HTTPException(400, "Configured storage provider does not support presigned URLs")
        return PresignedUrlResponse(
            url=url,
            method="GET",
            storage_key=asset.storage_key,
            expires_in=ttl,
        )
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
