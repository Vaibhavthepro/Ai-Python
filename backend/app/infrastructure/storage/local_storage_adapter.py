import os
import aiofiles
from app.domain.ports.storage_service import IStorageService

class LocalDiskStorageAdapter(IStorageService):
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save(self, key: str, content: bytes, content_type: str = "text/plain") -> str:
        file_path = os.path.join(self.base_path, key)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        return key

    async def read(self, key: str) -> bytes:
        file_path = os.path.join(self.base_path, key)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Key {key} not found")
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def delete(self, key: str) -> None:
        file_path = os.path.join(self.base_path, key)
        if os.path.exists(file_path):
            os.remove(file_path)

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        # In local storage, we just return an app route
        return f"/api/v1/storage/{key}"
