from app.core.config import settings
from app.domain.ports.storage_service import IStorageService
from app.infrastructure.storage.local_storage_adapter import LocalDiskStorageAdapter

def get_storage_service() -> IStorageService:
    if settings.STORAGE_BACKEND == "s3":
        # placeholder for S3
        pass
    return LocalDiskStorageAdapter(settings.LOCAL_STORAGE_PATH)
