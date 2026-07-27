from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr

from app.domain.media.service import MediaError, MediaService, SUPPORTED, detected_mime
from app.domain.media.storage import LocalStorageProvider, S3StorageProvider, storage_provider


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


@pytest.mark.asyncio
async def test_local_storage_does_not_issue_presigned_urls(tmp_path: Path) -> None:
    provider = LocalStorageProvider(tmp_path)

    assert not provider.supports_signed_urls()
    assert await provider.signed_download_url("owner/asset", 900) is None
    assert await provider.signed_upload_url("owner/asset", "image/jpeg", 900) is None


def test_storage_provider_selects_local_minio_and_s3(tmp_path: Path, monkeypatch) -> None:
    clients = []

    def fake_client(*_, **kwargs):
        clients.append(kwargs)
        return FakeS3Client()

    monkeypatch.setattr("boto3.client", fake_client)

    local = storage_provider(
        SimpleNamespace(media_storage_provider="local", media_storage_path=tmp_path)
    )
    assert isinstance(local, LocalStorageProvider)

    minio = storage_provider(settings("minio", tmp_path))
    s3 = storage_provider(settings("s3", tmp_path))

    assert isinstance(minio, S3StorageProvider)
    assert minio.name == "minio"
    assert isinstance(s3, S3StorageProvider)
    assert s3.name == "s3"
    assert clients[0]["endpoint_url"] == "http://minio:9000"
    assert clients[1]["endpoint_url"] is None


@pytest.mark.asyncio
async def test_s3_storage_provider_generates_presigned_upload_and_download_urls(monkeypatch):
    client = FakeS3Client()
    monkeypatch.setattr("boto3.client", lambda *_, **__: client)

    provider = S3StorageProvider(
        bucket="media",
        access_key_id="key",
        secret_access_key="secret",
        endpoint_url="http://minio:9000",
        retry_attempts=2,
        name="minio",
    )

    upload_url = await provider.signed_upload_url("owner/asset", "image/jpeg", 900)
    download_url = await provider.signed_download_url("owner/asset", 900)

    assert provider.supports_signed_urls()
    assert upload_url == "https://storage.example/put_object/owner/asset"
    assert download_url == "https://storage.example/get_object/owner/asset"
    assert client.presigned_calls[0]["Params"]["ContentType"] == "image/jpeg"
    assert client.presigned_calls[1]["ExpiresIn"] == 900


@pytest.mark.asyncio
async def test_s3_healthcheck_verifies_bucket_exists(monkeypatch):
    client = FakeS3Client()
    monkeypatch.setattr("boto3.client", lambda *_, **__: client)
    provider = S3StorageProvider(bucket="media", access_key_id="key", secret_access_key="secret")

    assert await provider.healthcheck()
    assert client.head_bucket_calls == [{"Bucket": "media"}]


class FakeS3Client:
    def __init__(self):
        self.presigned_calls = []
        self.head_bucket_calls = []

    def generate_presigned_url(self, operation, **kwargs):
        self.presigned_calls.append({"operation": operation, **kwargs})
        return f"https://storage.example/{operation}/{kwargs['Params']['Key']}"

    def head_bucket(self, **kwargs):
        self.head_bucket_calls.append(kwargs)
        return {}


def settings(provider: str, tmp_path: Path):
    return SimpleNamespace(
        media_storage_provider=provider,
        media_storage_path=tmp_path,
        s3_bucket="media",
        s3_access_key_id="key",
        s3_secret_access_key=SecretStr("secret"),
        s3_endpoint_url="http://minio:9000",
        s3_region="us-east-1",
        media_storage_timeout_seconds=30,
        media_storage_retry_attempts=3,
    )


class FinalizeDB:
    def __init__(self):
        self.added = []
        self.commits = 0

    def add(self, value):
        self.added.append(value)

    async def flush(self):
        return None

    async def commit(self):
        self.commits += 1


class FinalizeRepo:
    def __init__(self, existing=None):
        self.existing = existing

    async def by_storage_key(self, storage_key):
        return self.existing

    async def add(self, asset):
        self.existing = asset


class FinalizeStorage:
    name = "minio"

    def __init__(self, data: bytes):
        self.data = data
        self.deleted = []

    async def download(self, key):
        yield self.data

    async def delete(self, key):
        self.deleted.append(key)


@pytest.mark.asyncio
async def test_presigned_finalize_creates_asset_and_enqueues_processing(monkeypatch):
    import app.domain.media.tasks as tasks_module

    owner = uuid4()
    db = FinalizeDB()
    service = MediaService(db, FinalizeStorage(b"\xff\xd8\xffdata"))
    service.repo = FinalizeRepo()
    calls = []

    monkeypatch.setattr(
        tasks_module.process_media, "delay", lambda asset_id: calls.append(asset_id)
    )

    asset = await service.finalize_upload(
        owner,
        f"{owner}/upload",
        "My Photo.jpg",
        "image/jpeg",
    )

    assert asset.original_filename == "My_Photo.jpg"
    assert asset.upload_status == "UPLOADED"
    assert asset.processing_state == "QUEUED"
    assert db.commits == 1
    assert service.repo.existing is asset
    assert calls == [str(asset.id)]


@pytest.mark.asyncio
async def test_presigned_finalize_rejects_wrong_owner_and_mime():
    db = FinalizeDB()
    service = MediaService(db, FinalizeStorage(b"\x89PNG\r\n\x1a\npayload"))
    service.repo = FinalizeRepo()

    with pytest.raises(MediaError, match="Invalid storage key"):
        await service.finalize_upload(uuid4(), "someone-else/upload", "x.png", "image/png")

    with pytest.raises(MediaError, match="Uploaded media type does not match request"):
        await service.finalize_upload(
            UUID("123e4567-e89b-12d3-a456-426614174000"),
            "123e4567-e89b-12d3-a456-426614174000/upload",
            "x.jpg",
            "image/jpeg",
        )
