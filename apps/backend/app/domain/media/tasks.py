import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import get_settings
from app.domain.media.models import MediaVariant
from app.domain.media.processing import ImageProcessor
from app.domain.media.repository import MediaRepository
from app.domain.media.storage import LocalStorageProvider
from app.infrastructure.celery_app import celery_app
from app.infrastructure.database import create_database_engine


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
            try:
                asset.processing_state = "PROCESSING"
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
                        asset, LocalStorageProvider(settings.media_storage_path)
                    ):
                        await repo.add_variant(variant)
                asset.processing_state = "READY"
                await db.commit()
            except Exception:
                await db.rollback()
                asset = await repo.by_id(asset_id)
                if asset:
                    asset.processing_state, asset.upload_status = "FAILED", "FAILED"
                    await db.commit()
                raise
    finally:
        await engine.dispose()


@celery_app.task(name="media.process")
def process_media(asset_id: str) -> None:
    asyncio.run(process_media_asset(UUID(asset_id)))
