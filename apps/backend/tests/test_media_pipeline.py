import io
import subprocess
from uuid import uuid4

import pytest
from PIL import Image

from app.domain.media.models import MediaAsset
from app.domain.media.processing import ImageProcessor, VideoProcessor
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
async def test_image_processor_creates_configured_jpeg_and_webp_metadata():
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
    variants = await ImageProcessor().process(
        asset,
        storage,
        (("LARGE", 1600), ("THUMBNAIL", 400)),
        jpeg_quality=85,
        webp_quality=82,
    )
    assert [variant.kind for variant in variants] == [
        "LARGE_JPG",
        "LARGE_WEBP",
        "THUMBNAIL_JPG",
        "THUMBNAIL_WEBP",
    ]
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


@pytest.mark.asyncio
async def test_video_processor_extracts_metadata_and_generates_variants(tmp_path):
    asset = MediaAsset(
        id=uuid4(),
        owner_user_id=uuid4(),
        storage_key="owner/video",
        original_filename="clip.mp4",
        mime_type="video/mp4",
        media_type="VIDEO",
        file_size_bytes=5,
        checksum_sha256="checksum",
        upload_status="UPLOADED",
        processing_state="PROCESSING",
    )
    storage = Storage({asset.storage_key: b"video"})
    processor = FakeVideoProcessor()

    variants = await processor.process(
        asset,
        storage,
        display_max_px=1280,
        thumbnail_max_px=640,
        thumbnail_second=1,
    )

    assert asset.width == 1920
    assert asset.height == 1080
    assert asset.duration_ms == 2500
    assert asset.codec == "h264"
    assert asset.aspect_ratio == "1920:1080"
    assert [variant.kind for variant in variants] == ["DISPLAY", "THUMBNAIL"]
    assert variants[0].mime_type == "video/mp4"
    assert variants[1].mime_type == "image/jpeg"
    assert storage.values["owner/video.display.mp4"] == b"display"
    assert storage.values["owner/video.thumbnail.jpg"].startswith(b"\xff\xd8")
    assert [command[0] for command in processor.commands] == ["ffprobe", "ffmpeg", "ffmpeg"]


def test_media_processing_is_registered_as_a_worker_task():
    assert process_media.name == "media.process"


class FakeVideoProcessor(VideoProcessor):
    def __init__(self):
        self.commands = []

    async def _run(self, *command: str, capture_output: bool = False):
        self.commands.append(command)
        if command[0] == "ffprobe":
            return subprocess.CompletedProcess(
                command,
                0,
                b'{"streams":[{"width":1920,"height":1080,"codec_name":"h264"}],'
                b'"format":{"duration":"2.5"}}',
                b"",
            )
        output = command[-1]
        if output.endswith(".mp4"):
            with open(output, "wb") as file:
                file.write(b"display")
        if output.endswith(".jpg"):
            Image.new("RGB", (640, 360), "blue").save(output, format="JPEG")
        return subprocess.CompletedProcess(command, 0, b"", b"")
