from abc import ABC, abstractmethod
from app.domain.entities.models import ExecutionResult

class ICodeExecutor(ABC):
    @abstractmethod
    async def execute(self, code: str, job_id: str) -> ExecutionResult:
        """Execute code and return the result."""
        pass
