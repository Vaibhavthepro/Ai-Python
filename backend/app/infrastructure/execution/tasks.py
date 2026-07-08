from app.worker import celery_app
from app.infrastructure.execution.docker_executor import DockerCodeExecutor
import asyncio

# Since celery task is synchronous, we can run async code inside it using asyncio.run
@celery_app.task(name="execute_code_task")
def execute_code_task(code: str, job_id: str):
    executor = DockerCodeExecutor()
    # Using the sync inner method directly to avoid nested event loop issues in celery
    result = executor._execute_sync(code, job_id)
    return result.model_dump()
