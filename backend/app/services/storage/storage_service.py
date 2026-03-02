"""
Storage abstraction layer.
"""

import os
import uuid
from abc import ABC, abstractmethod

from app.core.config import get_settings

settings = get_settings()


# ── Abstract Interface
class StorageService(ABC):
    @abstractmethod
    async def upload_file(
        self, file_bytes: bytes, filename: str, content_type: str
    ) -> str:
        """Upload and return the storage key."""

    @abstractmethod
    async def get_url(self, key: str) -> str:
        """Return a publicly accessible (or presigned) URL."""

    @abstractmethod
    async def delete_file(self, key: str) -> None:
        """Delete a stored object."""

    @abstractmethod
    async def read_file(self, key: str) -> bytes:
        """Return raw bytes of a stored object."""


# ── Local Filesystem Implementation (testing)


class LocalStorageService(StorageService):
    def __init__(self) -> None:
        self._base = settings.LOCAL_STORAGE_PATH
        os.makedirs(self._base, exist_ok=True)

    async def upload_file(
        self, file_bytes: bytes, filename: str, content_type: str
    ) -> str:
        key = f"{uuid.uuid4()}-{filename}"
        with open(os.path.join(self._base, key), "wb") as f:
            f.write(file_bytes)
        return key

    async def get_url(self, key: str) -> str:
        return f"file://{self._base}/{key}"

    async def delete_file(self, key: str) -> None:
        path = os.path.join(self._base, key)
        if os.path.exists(path):
            os.remove(path)

    async def read_file(self, key: str) -> bytes:
        with open(os.path.join(self._base, key), "rb") as f:
            return f.read()


def get_storage_service() -> StorageService:
    """FastAPI dependency – returns the configured storage backend."""
    backend = settings.STORAGE_BACKEND
    if backend == "local":
        return LocalStorageService()
    # we can add miltiple storage backends here (e.g. AWS S3) following the same pattern
    raise ValueError(f"Unknown STORAGE_BACKEND: {backend}")
