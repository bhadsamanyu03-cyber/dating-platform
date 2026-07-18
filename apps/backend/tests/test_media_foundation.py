from pathlib import Path

import pytest

from app.domain.media.service import SUPPORTED, detected_mime
from app.domain.media.storage import LocalStorageProvider


@pytest.mark.parametrize(
    ("content", "mime"),
    [
        (b"\xff\xd8\xffimage", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\nimage", "image/png"),
        (b"RIFFxxxxWEBPimage", "image/webp"),
        (b"\x00\x00\x00\x18ftypisomvideo", "video/mp4"),
        (b"\x00\x00\x00\x18ftypqt  video", "video/quicktime"),
    ],
)
def test_supported_media_is_detected_from_content(content: bytes, mime: str) -> None:
    assert detected_mime(content) == mime
    assert SUPPORTED[mime] in {"IMAGE", "VIDEO"}


def test_unknown_content_is_rejected() -> None:
    assert detected_mime(b"not-media") is None


@pytest.mark.asyncio
async def test_local_storage_upload_download_metadata_and_delete(tmp_path: Path) -> None:
    provider = LocalStorageProvider(tmp_path)

    async def chunks():
        yield b"hello "
        yield b"media"

    size, checksum = await provider.upload("owner/asset", chunks())
    assert size == 11 and len(checksum) == 64
    assert await provider.exists("owner/asset")
    assert await provider.metadata("owner/asset") == {"size": 11}
    assert b"".join([chunk async for chunk in provider.download("owner/asset")]) == b"hello media"
    await provider.delete("owner/asset")
    assert not await provider.exists("owner/asset")


def test_local_storage_rejects_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        LocalStorageProvider(tmp_path).path("../../outside")
