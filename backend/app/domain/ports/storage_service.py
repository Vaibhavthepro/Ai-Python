from abc import ABC, abstractmethod

class IStorageService(ABC):
    @abstractmethod
    async def save(self, key: str, content: bytes, content_type: str) -> str:
        """Persist content, return a retrievable URI/reference."""
        pass

    @abstractmethod
    async def read(self, key: str) -> bytes:
        """Retrieve content by key."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove content by key."""
        pass

    @abstractmethod
    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Return a temporary shareable URL (local: signed app route; S3: presigned URL)."""
        pass
