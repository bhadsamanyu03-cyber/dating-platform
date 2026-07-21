import io
from collections.abc import AsyncIterator

from PIL import Image, ImageOps

from app.domain.media.models import MediaAsset, MediaVariant
from app.domain.media.storage import StorageProvider


class ImageProcessor:
    """Storage-agnostic synchronous processing boundary for future worker execution."""

    async def process(self, asset: MediaAsset, storage: StorageProvider) -> list[MediaVariant]:
        raw = b"".join([chunk async for chunk in storage.download(asset.storage_key)])
        with Image.open(io.BytesIO(raw)) as source:
            orientation = source.getexif().get(274)
            image = ImageOps.exif_transpose(source).convert("RGB")
            asset.width, asset.height, asset.orientation = image.width, image.height, orientation
            asset.aspect_ratio = f"{image.width}:{image.height}"
            variants = []
            for kind, maximum in (("DISPLAY", 1600), ("THUMBNAIL", 400)):
                rendered = image.copy()
                rendered.thumbnail((maximum, maximum))
                output = io.BytesIO()
                rendered.save(output, format="JPEG", quality=85, optimize=True)
                key = f"{asset.storage_key}.{kind.lower()}.jpg"

                async def chunks(value=output.getvalue()) -> AsyncIterator[bytes]:
                    yield value

                size, _ = await storage.upload(key, chunks())
                variants.append(
                    MediaVariant(
                        media_asset_id=asset.id,
                        kind=kind,
                        storage_key=key,
                        mime_type="image/jpeg",
                        width=rendered.width,
                        height=rendered.height,
                        file_size_bytes=size,
                    )
                )
            return variants
