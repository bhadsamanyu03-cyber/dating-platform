from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.media import tasks
from app.domain.media.models import MediaAsset


class FakeDatabase:
    def __init__(self, asset):
        self.asset = asset
        self.commits = 0
        self.rollbacks = 0

    async def commit(self):
        self.commits += 1

    async def rollback(self):
        self.rollbacks += 1

    async def refresh(self, _):
        pass


class FakeSession:
    def __init__(self, database):
        self.database = database

    async def __aenter__(self):
        return self.database

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeEngine:
    async def dispose(self):
        pass


class FakeRepository:
    def __init__(self, database):
        self.database = database

    async def by_id(self, asset_id):
        return self.database.asset if self.database.asset.id == asset_id else None

    async def has_variants(self, _):
        return False

    async def add_variant(self, _):
        pass


class RetryableImageProcessor:
    async def process(self, *_args, **_kwargs):
        raise OSError("temporary storage outage")


class PermanentImageProcessor:
    async def process(self, *_args, **_kwargs):
        raise ValueError("corrupt upload")


def _asset():
    return MediaAsset(
        id=uuid4(),
        owner_user_id=uuid4(),
        storage_key="owner/image",
        original_filename="photo.jpg",
        mime_type="image/jpeg",
        media_type="IMAGE",
        file_size_bytes=1024,
        checksum_sha256="checksum",
        upload_status="UPLOADED",
        processing_state="QUEUED",
    )


@pytest.mark.asyncio
async def test_transient_processing_failure_is_retained_for_retry(monkeypatch):
    asset = _asset()
    database = FakeDatabase(asset)

    monkeypatch.setattr(tasks, "create_database_engine", lambda *_args, **_kwargs: FakeEngine())
    monkeypatch.setattr(
        tasks, "async_sessionmaker", lambda *_args, **_kwargs: lambda: FakeSession(database)
    )
    monkeypatch.setattr(tasks, "MediaRepository", FakeRepository)
    monkeypatch.setattr(tasks, "ImageProcessor", RetryableImageProcessor)
    monkeypatch.setattr(
        tasks, "storage_provider", lambda *_args, **_kwargs: SimpleNamespace(name="s3")
    )
    monkeypatch.setattr(
        tasks,
        "get_settings",
        lambda: SimpleNamespace(
            database_url="postgresql://example",
            media_image_large_px=2048,
            media_image_medium_px=1280,
            media_image_small_px=640,
            media_thumbnail_px=320,
            media_image_jpeg_quality=85,
            media_image_webp_quality=82,
            media_video_display_px=1280,
            media_video_thumbnail_px=640,
            media_video_thumbnail_second=1,
            media_processing_stale_seconds=3600,
        ),
    )

    with pytest.raises(tasks.RetryableMediaProcessingError):
        await tasks.process_media_asset(asset.id)

    assert asset.processing_state == "QUEUED"
    assert asset.upload_status == "UPLOADED"
    assert database.commits == 1
    assert database.rollbacks == 1


@pytest.mark.asyncio
async def test_unrecoverable_processing_failure_marks_asset_failed(monkeypatch):
    asset = _asset()
    database = FakeDatabase(asset)

    monkeypatch.setattr(tasks, "create_database_engine", lambda *_args, **_kwargs: FakeEngine())
    monkeypatch.setattr(
        tasks, "async_sessionmaker", lambda *_args, **_kwargs: lambda: FakeSession(database)
    )
    monkeypatch.setattr(tasks, "MediaRepository", FakeRepository)
    monkeypatch.setattr(tasks, "ImageProcessor", PermanentImageProcessor)
    monkeypatch.setattr(
        tasks, "storage_provider", lambda *_args, **_kwargs: SimpleNamespace(name="s3")
    )
    monkeypatch.setattr(
        tasks,
        "get_settings",
        lambda: SimpleNamespace(
            database_url="postgresql://example",
            media_image_large_px=2048,
            media_image_medium_px=1280,
            media_image_small_px=640,
            media_thumbnail_px=320,
            media_image_jpeg_quality=85,
            media_image_webp_quality=82,
            media_video_display_px=1280,
            media_video_thumbnail_px=640,
            media_video_thumbnail_second=1,
            media_processing_stale_seconds=3600,
        ),
    )

    with pytest.raises(tasks.PermanentMediaProcessingError):
        await tasks.process_media_asset(asset.id)

    assert asset.processing_state == "FAILED"
    assert asset.upload_status == "FAILED"
    assert database.commits == 1
    assert database.rollbacks == 1
