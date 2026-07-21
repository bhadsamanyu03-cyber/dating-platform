import io
from uuid import uuid4

import pytest
from PIL import Image

from app.domain.media.models import MediaAsset
from app.domain.media.processing import ImageProcessor
from app.domain.media.tasks import process_media


class Storage:
    name = "test"

    def __init__(self, values):
        self.values = values

    async def download(self, key):
        yield self.values[key]

    async def upload(self, key, chunks):
        value = b"".join([chunk async for chunk in chunks])
        self.values[key] = value
        return len(value), "checksum"

    async def delete(self, key):
        self.values.pop(key, None)


@pytest.mark.asyncio
async def test_image_processor_creates_original_display_and_thumbnail_metadata():
    source = io.BytesIO()
    Image.new("RGB", (2000, 1000), "red").save(source, format="JPEG")
    asset = MediaAsset(
        id=uuid4(),
        owner_user_id=uuid4(),
        storage_key="owner/original",
        original_filename="photo.jpg",
        mime_type="image/jpeg",
        media_type="IMAGE",
        file_size_bytes=len(source.getvalue()),
        checksum_sha256="checksum",
        upload_status="UPLOADED",
        processing_state="PROCESSING",
    )
    storage = Storage({asset.storage_key: source.getvalue()})
    variants = await ImageProcessor().process(asset, storage)
    assert [variant.kind for variant in variants] == ["DISPLAY", "THUMBNAIL"]
    assert asset.width == 2000 and asset.height == 1000 and asset.aspect_ratio == "2000:1000"
    assert all(variant.storage_key in storage.values for variant in variants)


def test_media_metadata_states_and_video_support_are_explicit():
    asset = MediaAsset(
        id=uuid4(),
        owner_user_id=uuid4(),
        storage_key="owner/video",
        original_filename="clip.mp4",
        mime_type="video/mp4",
        media_type="VIDEO",
        file_size_bytes=1,
        checksum_sha256="checksum",
        upload_status="UPLOADED",
        processing_state="READY",
        duration_ms=1000,
        width=1920,
        height=1080,
        aspect_ratio="16:9",
        codec="h264",
    )
    assert asset.processing_state == "READY" and asset.media_type == "VIDEO"


def test_media_processing_is_registered_as_a_worker_task():
    assert process_media.name == "media.process"
