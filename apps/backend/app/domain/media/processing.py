import io
from collections.abc import AsyncIterator

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
