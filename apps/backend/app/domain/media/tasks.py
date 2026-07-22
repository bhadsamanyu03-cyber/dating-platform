import asyncio
import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import get_settings
from app.domain.media.models import MediaVariant
from app.domain.media.processing import ImageProcessor, VideoProcessor
from app.domain.media.repository import MediaRepository
from app.domain.media.storage import storage_provider
from app.domain.identity.security import utcnow
from app.infrastructure.celery_app import celery_app
from app.infrastructure.database import create_database_engine

logger = logging.getLogger(__name__)


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
            try:
                asset.processing_state = "PROCESSING"
                if not await repo.has_variants(asset.id):
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
                    for variant in await VideoProcessor().process(
                        asset,
                        storage_provider(settings),
                        display_max_px=settings.media_video_display_px,
                        thumbnail_max_px=settings.media_video_thumbnail_px,
                        thumbnail_second=settings.media_video_thumbnail_second,
                    ):
                        await repo.add_variant(variant)
                asset.processing_state = "READY"
                await db.commit()
            except Exception:
                logger.exception("media_processing_failed", extra={"media_asset_id": str(asset_id)})
                await db.rollback()
                asset = await repo.by_id(asset_id)
                if asset:
                    asset.processing_state, asset.upload_status = "FAILED", "FAILED"
                    await db.commit()
                raise
    finally:
        await engine.dispose()


@celery_app.task(
    name="media.process",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def process_media(asset_id: str) -> None:
    asyncio.run(process_media_asset(UUID(asset_id)))


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
