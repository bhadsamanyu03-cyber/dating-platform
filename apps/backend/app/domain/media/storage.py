import hashlib
from collections.abc import AsyncIterator
from pathlib import Path


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

    async def metadata(self, key: str) -> dict:
        return {"size": self.path(key).stat().st_size}
