import asyncio
import hashlib
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Protocol

from app.core.config import Settings


class StorageError(RuntimeError):
    """A provider failure that can be handled without leaking provider details."""


class StorageProvider(Protocol):
    name: str

    async def upload(self, key: str, chunks: AsyncIterator[bytes]) -> tuple[int, str]: ...

    async def download(self, key: str) -> AsyncIterator[bytes]: ...

    async def delete(self, key: str) -> None: ...

    async def exists(self, key: str) -> bool: ...

    async def metadata(self, key: str) -> dict[str, int]: ...

    async def healthcheck(self) -> bool: ...

    def supports_signed_urls(self) -> bool: ...

    async def signed_download_url(self, key: str, expires_in: int) -> str | None: ...

    async def signed_upload_url(
        self, key: str, content_type: str, expires_in: int
    ) -> str | None: ...


class LocalStorageProvider:
    name = "local"

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, key: str) -> Path:
        candidate = (self.root / key).resolve()
        if self.root not in candidate.parents:
            raise ValueError("Invalid storage key")
        return candidate

    async def upload(self, key: str, chunks: AsyncIterator[bytes]) -> tuple[int, str]:
        path = self.path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError(key)
        digest, size = hashlib.sha256(), 0
        with path.open("xb") as file:
            async for chunk in chunks:
                digest.update(chunk)
                size += len(chunk)
                file.write(chunk)
        return size, digest.hexdigest()

    async def download(self, key: str) -> AsyncIterator[bytes]:
        with self.path(key).open("rb") as file:
            while chunk := file.read(1024 * 1024):
                yield chunk

    async def delete(self, key: str) -> None:
        self.path(key).unlink(missing_ok=True)

    async def exists(self, key: str) -> bool:
        return self.path(key).is_file()

    async def metadata(self, key: str) -> dict[str, int]:
        return {"size": self.path(key).stat().st_size}

    async def healthcheck(self) -> bool:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            return self.root.is_dir()
        except OSError:
            return False

    def supports_signed_urls(self) -> bool:
        return False

    async def signed_download_url(self, key: str, expires_in: int) -> str | None:
        return None

    async def signed_upload_url(self, key: str, content_type: str, expires_in: int) -> str | None:
        return None


class S3StorageProvider:
    """S3-compatible provider used by both AWS S3 and MinIO.

    boto3 is deliberately isolated here so domain services stay provider-agnostic.
    """

    name = "s3"

    def __init__(
        self,
        *,
        bucket: str,
        access_key_id: str,
        secret_access_key: str,
        endpoint_url: str | None = None,
        region_name: str = "us-east-1",
        timeout_seconds: int = 30,
        retry_attempts: int = 3,
        name: str = "s3",
    ):
        import boto3
        from botocore.config import Config

        self.name = name
        self.bucket = bucket
        self.retry_attempts = retry_attempts
        self.timeout_seconds = timeout_seconds
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or None,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
            config=Config(
                connect_timeout=timeout_seconds,
                read_timeout=timeout_seconds,
                retries={"max_attempts": retry_attempts, "mode": "standard"},
            ),
        )

    async def _call(self, operation, *args, **kwargs):
        from botocore.exceptions import BotoCoreError, ClientError

        last_error: Exception | None = None
        for attempt in range(self.retry_attempts):
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(operation, *args, **kwargs),
                    timeout=self.timeout_seconds,
                )
            except TimeoutError as error:
                last_error = error
                if attempt + 1 >= self.retry_attempts:
                    break
                await asyncio.sleep(min(0.1 * (2**attempt), 1.0))
            except (BotoCoreError, ClientError) as error:
                last_error = error
                if attempt + 1 >= self.retry_attempts:
                    break
                await asyncio.sleep(min(0.1 * (2**attempt), 1.0))
        raise StorageError("Storage provider operation failed") from last_error

    async def upload(self, key: str, chunks: AsyncIterator[bytes]) -> tuple[int, str]:
        value = b"".join([chunk async for chunk in chunks])
        checksum = hashlib.sha256(value).hexdigest()
        await self._call(self.client.put_object, Bucket=self.bucket, Key=key, Body=value)
        return len(value), checksum

    async def download(self, key: str) -> AsyncIterator[bytes]:
        response = await self._call(self.client.get_object, Bucket=self.bucket, Key=key)
        body = response["Body"]
        try:
            while chunk := await asyncio.to_thread(body.read, 1024 * 1024):
                yield chunk
        finally:
            await asyncio.to_thread(body.close)

    async def delete(self, key: str) -> None:
        await self._call(self.client.delete_object, Bucket=self.bucket, Key=key)

    async def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError

        last_error: Exception | None = None
        for attempt in range(self.retry_attempts):
            try:
                await asyncio.to_thread(self.client.head_object, Bucket=self.bucket, Key=key)
                return True
            except ClientError as error:
                if error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404:
                    return False
                last_error = error
                if attempt + 1 < self.retry_attempts:
                    await asyncio.sleep(min(0.1 * (2**attempt), 1.0))
        raise StorageError("Unable to inspect storage object") from last_error

    async def metadata(self, key: str) -> dict[str, int]:
        result = await self._call(self.client.head_object, Bucket=self.bucket, Key=key)
        return {"size": int(result["ContentLength"])}

    async def healthcheck(self) -> bool:
        try:
            await self._call(self.client.head_bucket, Bucket=self.bucket)
            return True
        except StorageError:
            return False

    def supports_signed_urls(self) -> bool:
        return True

    async def signed_download_url(self, key: str, expires_in: int) -> str | None:
        return await self._call(
            self.client.generate_presigned_url,
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    async def signed_upload_url(self, key: str, content_type: str, expires_in: int) -> str | None:
        return await self._call(
            self.client.generate_presigned_url,
            "put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expires_in,
        )


def storage_provider(settings: Settings) -> StorageProvider:
    if settings.media_storage_provider == "local":
        return LocalStorageProvider(settings.media_storage_path)
    return S3StorageProvider(
        bucket=settings.s3_bucket,
        access_key_id=settings.s3_access_key_id,
        secret_access_key=settings.s3_secret_access_key.get_secret_value(),
        endpoint_url=(
            settings.s3_endpoint_url if settings.media_storage_provider == "minio" else None
        ),
        region_name=settings.s3_region,
        timeout_seconds=settings.media_storage_timeout_seconds,
        retry_attempts=settings.media_storage_retry_attempts,
        name=settings.media_storage_provider,
    )
