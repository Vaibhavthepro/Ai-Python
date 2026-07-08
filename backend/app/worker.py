from celery import Celery
from app.core.config import settings
import os

# We read from env directly if settings.REDIS_URL is not fully available at import time
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("executor_worker", broker=redis_url, backend=redis_url, include=["app.infrastructure.execution.tasks"])

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
