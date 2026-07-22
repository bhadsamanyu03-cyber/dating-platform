import asyncio
import io
import json
import subprocess
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path

from PIL import Image, ImageOps

from app.domain.media.models import MediaAsset, MediaVariant
from app.domain.media.storage import StorageProvider


class ImageProcessor:
    """Storage-agnostic synchronous processing boundary for future worker execution."""

    async def process(
        self,
        asset: MediaAsset,
        storage: StorageProvider,
        presets: tuple[tuple[str, int], ...],
        jpeg_quality: int,
        webp_quality: int,
    ) -> list[MediaVariant]:
        raw = b"".join([chunk async for chunk in storage.download(asset.storage_key)])
        with Image.open(io.BytesIO(raw)) as source:
            orientation = source.getexif().get(274)
            image = ImageOps.exif_transpose(source).convert("RGB")
            asset.width, asset.height, asset.orientation = image.width, image.height, orientation
            asset.aspect_ratio = f"{image.width}:{image.height}"
            variants = []
            for kind, maximum in presets:
                rendered = image.copy()
                rendered.thumbnail((maximum, maximum))
                for suffix, image_format, mime_type, quality in (
                    ("jpg", "JPEG", "image/jpeg", jpeg_quality),
                    ("webp", "WEBP", "image/webp", webp_quality),
                ):
                    output = io.BytesIO()
                    rendered.save(output, format=image_format, quality=quality, optimize=True)
                    key = f"{asset.storage_key}.{kind.lower()}.{suffix}"

                    async def chunks(value=output.getvalue()) -> AsyncIterator[bytes]:
                        yield value

                    size, _ = await storage.upload(key, chunks())
                    variants.append(
                        MediaVariant(
                            media_asset_id=asset.id,
                            kind=f"{kind}_{suffix.upper()}",
                            storage_key=key,
                            mime_type=mime_type,
                            width=rendered.width,
                            height=rendered.height,
                            file_size_bytes=size,
                        )
                    )
            return variants


class VideoProcessor:
    """Extract video metadata and generate storage-backed display/thumbnail variants."""

    async def process(
        self,
        asset: MediaAsset,
        storage: StorageProvider,
        *,
        display_max_px: int,
        thumbnail_max_px: int,
        thumbnail_second: int,
    ) -> list[MediaVariant]:
        raw = b"".join([chunk async for chunk in storage.download(asset.storage_key)])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            display = root / "display.mp4"
            thumbnail = root / "thumbnail.jpg"
            source.write_bytes(raw)
            metadata = await self._probe(source)
            asset.width = metadata.width
            asset.height = metadata.height
            asset.duration_ms = metadata.duration_ms
            asset.codec = metadata.codec
            asset.aspect_ratio = (
                f"{metadata.width}:{metadata.height}"
                if metadata.width and metadata.height
                else None
            )
            await self._run(
                "ffmpeg",
                "-y",
                "-i",
                str(source),
                "-vf",
                f"scale='min({display_max_px},iw)':-2",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-movflags",
                "+faststart",
                "-an",
                str(display),
            )
            await self._run(
                "ffmpeg",
                "-y",
                "-ss",
                str(thumbnail_second),
                "-i",
                str(source),
                "-frames:v",
                "1",
                "-vf",
                f"scale='min({thumbnail_max_px},iw)':-2",
                str(thumbnail),
            )
            return [
                await self._variant(asset, storage, "DISPLAY", display, "video/mp4"),
                await self._variant(asset, storage, "THUMBNAIL", thumbnail, "image/jpeg"),
            ]

    async def _probe(self, source: Path) -> "VideoMetadata":
        result = await self._run(
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,codec_name:format=duration",
            "-of",
            "json",
            str(source),
            capture_output=True,
        )
        data = json.loads(result.stdout.decode())
        stream = (data.get("streams") or [{}])[0]
        duration = float((data.get("format") or {}).get("duration") or 0)
        return VideoMetadata(
            width=stream.get("width"),
            height=stream.get("height"),
            duration_ms=round(duration * 1000) if duration else None,
            codec=stream.get("codec_name"),
        )

    async def _variant(
        self, asset: MediaAsset, storage: StorageProvider, kind: str, path: Path, mime_type: str
    ) -> MediaVariant:
        key = f"{asset.storage_key}.{kind.lower()}{path.suffix}"

        async def chunks() -> AsyncIterator[bytes]:
            with path.open("rb") as file:
                while chunk := file.read(1024 * 1024):
                    yield chunk

        size, _ = await storage.upload(key, chunks())
        width = height = None
        if mime_type.startswith("image/"):
            with Image.open(path) as image:
                width, height = image.width, image.height
        else:
            width, height = asset.width, asset.height
        return MediaVariant(
            media_asset_id=asset.id,
            kind=kind,
            storage_key=key,
            mime_type=mime_type,
            width=width,
            height=height,
            file_size_bytes=size,
        )

    async def _run(
        self, *command: str, capture_output: bool = False
    ) -> subprocess.CompletedProcess:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode:
            raise RuntimeError(stderr.decode().strip() or f"{command[0]} failed")
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


class VideoMetadata:
    def __init__(
        self,
        *,
        width: int | None,
        height: int | None,
        duration_ms: int | None,
        codec: str | None,
    ):
        self.width = width
        self.height = height
        self.duration_ms = duration_ms
        self.codec = codec
