import re
from pathlib import Path
from uuid import UUID, uuid4
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.media.models import MediaAsset, MediaVariant
from app.domain.media.processing import ImageProcessor
from app.domain.media.repository import MediaRepository
from app.domain.media.schemas import MediaMetadata
from app.domain.media.storage import StorageProvider

SUPPORTED = {
    "image/jpeg": "IMAGE",
    "image/png": "IMAGE",
    "image/webp": "IMAGE",
    "image/heic": "IMAGE",
    "video/mp4": "VIDEO",
    "video/quicktime": "VIDEO",
}
LIMITS = {"IMAGE": 25 * 1024 * 1024, "VIDEO": 100 * 1024 * 1024}


def detected_mime(header: bytes) -> str | None:
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image/webp"
    if header[4:8] == b"ftyp":
        brand = header[8:12].lower()
        if brand in {b"heic", b"heix", b"hevc", b"hevx"}:
            return "image/heic"
        return "video/quicktime" if brand == b"qt  " else "video/mp4"
    return None


class MediaError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status_code = message, status


class MediaService:
    def __init__(self, db: AsyncSession, storage: StorageProvider, processor: ImageProcessor | None = None):
        self.db, self.repo, self.storage = db, MediaRepository(db), storage
        self.processor = processor or ImageProcessor()

    async def upload(self, owner: UUID, file: UploadFile) -> MediaAsset:
        first_chunk = await file.read(1024 * 1024)
        detected = detected_mime(first_chunk)
        media_type = SUPPORTED.get(detected or "")
        if not media_type:
            raise MediaError("Unsupported media type", 422)
        filename = Path(file.filename or "upload").name
        if not filename or filename in {".", ".."}:
            raise MediaError("Invalid filename", 422)
        key = f"{owner}/{uuid4().hex}"

        async def chunks():
            total = 0
            if first_chunk:
                total = len(first_chunk)
                if total > LIMITS[media_type]:
                    raise MediaError("File exceeds size limit", 422)
                yield first_chunk
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > LIMITS[media_type]:
                    raise MediaError("File exceeds size limit", 422)
                yield chunk

        asset = MediaAsset(
            owner_user_id=owner,
            storage_key=key,
            original_filename=re.sub(r"[^A-Za-z0-9._-]", "_", filename),
            mime_type=detected,
            media_type=media_type,
            file_size_bytes=0,
            checksum_sha256="",
            upload_status="UPLOADING",
            processing_state="UPLOADING",
        )
        await self.repo.add(asset)
        try:
            size, checksum = await self.storage.upload(key, chunks())
            if not size:
                raise MediaError("Empty uploads are not allowed", 422)
            asset.file_size_bytes, asset.checksum_sha256, asset.upload_status = size, checksum, "UPLOADED"
            asset.processing_state = "PROCESSING"
            await self.repo.add_variant(
                MediaVariant(
                    media_asset_id=asset.id,
                    kind="ORIGINAL",
                    storage_key=asset.storage_key,
                    mime_type=asset.mime_type,
                    width=None,
                    height=None,
                    file_size_bytes=size,
                )
            )
            if media_type == "IMAGE":
                for variant in await self.processor.process(asset, self.storage):
                    await self.repo.add_variant(variant)
            asset.processing_state = "READY"
            await self.db.commit()
            return asset
        except Exception:
            await self.storage.delete(key)
            asset.upload_status = "FAILED"
            asset.processing_state = "FAILED"
            await self.db.commit()
            raise

    async def get(self, asset_id: UUID, owner: UUID):
        asset = await self.repo.owned(asset_id, owner)
        if not asset:
            raise MediaError("Media asset not found", 404)
        return asset

    async def delete(self, asset_id: UUID, owner: UUID):
        asset = await self.get(asset_id, owner)
        await self.storage.delete(asset.storage_key)
        asset.upload_status = "DELETED"
        await self.db.commit()

    def metadata(self, asset):
        return MediaMetadata.model_validate(asset, from_attributes=True)
