import asyncio
import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import get_settings
from app.domain.identity.security import utcnow
from app.domain.media.models import MediaVariant
from app.domain.media.processing import ImageProcessor, VideoProcessor
from app.domain.media.repository import MediaRepository
from app.domain.media.storage import storage_provider
from app.infrastructure.celery_app import celery_app
from app.infrastructure.database import create_database_engine

logger = logging.getLogger(__name__)


class RetryableMediaProcessingError(RuntimeError):
    def __init__(self, stage: str, error: Exception):
        self.stage = stage
        self.error = error
        super().__init__(f"{stage}: {error}")


class PermanentMediaProcessingError(RuntimeError):
    def __init__(self, stage: str, error: Exception):
        self.stage = stage
        self.error = error
        super().__init__(f"{stage}: {error}")


def _is_retryable_media_processing_error(error: Exception, stage: str) -> bool:
    from PIL import UnidentifiedImageError

    from app.domain.media.storage import StorageError

    retryable_types = (
        StorageError,
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError,
        OSError,
        UnidentifiedImageError,
    )
    if isinstance(error, retryable_types):
        return True
    if isinstance(error, RuntimeError) and stage in {
        "download-original",
        "generate-image-variants",
        "generate-video-variants",
        "write-variants",
    }:
        return True
    return False


async def _mark_asset_failed(asset_id: UUID, stage: str, error: Exception) -> None:
    settings = get_settings()
    engine = create_database_engine(str(settings.database_url))
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as db:
            asset = await MediaRepository(db).by_id(asset_id)
            if asset and asset.upload_status != "DELETED":
                asset.processing_state, asset.upload_status = "FAILED", "FAILED"
                await db.commit()
                logger.error(
                    "media_processing_failed",
                    extra={
                        "media_asset_id": str(asset_id),
                        "processing_stage": stage,
                        "exception_type": type(error).__name__,
                        "exception_message": str(error),
                        "retryable": False,
                    },
                    exc_info=(type(error), error, error.__traceback__),
                )
    finally:
        await engine.dispose()


async def process_media_asset(asset_id: UUID) -> None:
    settings = get_settings()
    engine = create_database_engine(str(settings.database_url))
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as db:
            repo = MediaRepository(db)
            asset = await repo.by_id(asset_id)
            if not asset or asset.upload_status != "UPLOADED":
                return
            if asset.processing_state == "READY":
                return
            stage = "initializing"
            try:
                stage = "mark-processing"
                asset.processing_state = "PROCESSING"
                if not await repo.has_variants(asset.id):
                    stage = "register-original"
                    await repo.add_variant(
                        MediaVariant(
                            media_asset_id=asset.id,
                            kind="ORIGINAL",
                            storage_key=asset.storage_key,
                            mime_type=asset.mime_type,
                            width=asset.width,
                            height=asset.height,
                            file_size_bytes=asset.file_size_bytes,
                        )
                    )
                if asset.media_type == "IMAGE":
                    stage = "generate-image-variants"
                    for variant in await ImageProcessor().process(
                        asset,
                        storage_provider(settings),
                        (
                            ("LARGE", settings.media_image_large_px),
                            ("MEDIUM", settings.media_image_medium_px),
                            ("SMALL", settings.media_image_small_px),
                            ("THUMBNAIL", settings.media_thumbnail_px),
                        ),
                        settings.media_image_jpeg_quality,
                        settings.media_image_webp_quality,
                    ):
                        await repo.add_variant(variant)
                if asset.media_type == "VIDEO":
                    stage = "generate-video-variants"
                    for variant in await VideoProcessor().process(
                        asset,
                        storage_provider(settings),
                        display_max_px=settings.media_video_display_px,
                        thumbnail_max_px=settings.media_video_thumbnail_px,
                        thumbnail_second=settings.media_video_thumbnail_second,
                    ):
                        await repo.add_variant(variant)
                stage = "finalize"
                asset.processing_state = "READY"
                await db.commit()
            except Exception as error:
                await db.rollback()
                retryable = _is_retryable_media_processing_error(error, stage)
                logger_fn = logger.warning if retryable else logger.error
                logger_fn(
                    "media_processing_retryable" if retryable else "media_processing_failed",
                    extra={
                        "media_asset_id": str(asset_id),
                        "processing_stage": stage,
                        "exception_type": type(error).__name__,
                        "exception_message": str(error),
                        "retryable": retryable,
                    },
                    exc_info=True,
                )
                asset = await repo.by_id(asset_id)
                if asset and asset.upload_status != "DELETED":
                    if retryable:
                        asset.processing_state = "QUEUED"
                    else:
                        asset.processing_state, asset.upload_status = "FAILED", "FAILED"
                    await db.commit()
                if retryable:
                    raise RetryableMediaProcessingError(stage, error) from error
                raise PermanentMediaProcessingError(stage, error) from error
    finally:
        await engine.dispose()


@celery_app.task(name="media.process", bind=True, max_retries=3)
def process_media(self, asset_id: str) -> None:
    try:
        asyncio.run(process_media_asset(UUID(asset_id)))
    except RetryableMediaProcessingError as error:
        if self.request.retries >= self.max_retries:
            asyncio.run(_mark_asset_failed(UUID(asset_id), error.stage, error.error))
            raise PermanentMediaProcessingError(error.stage, error.error) from error
        countdown = min(2**self.request.retries, 30)
        raise self.retry(exc=error, countdown=countdown) from error


@celery_app.task(name="media.recover_stale")
def recover_stale_media() -> int:
    """Requeue work abandoned by a worker crash; safe to run periodically."""

    async def recover() -> int:
        settings = get_settings()
        engine = create_database_engine(str(settings.database_url))
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as db:
                assets = await MediaRepository(db).stale_processing(
                    utcnow() - timedelta(seconds=settings.media_processing_stale_seconds)
                )
                for asset in assets:
                    asset.processing_state = "QUEUED"
                await db.commit()
                for asset in assets:
                    process_media.delay(str(asset.id))
                return len(assets)
        finally:
            await engine.dispose()

    return asyncio.run(recover())
