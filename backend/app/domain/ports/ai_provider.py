from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List

class GeneratedCodeResponse(BaseModel):
    code: str
    explanation: str
    imports: List[str]

class IAIProvider(ABC):
    @abstractmethod
    async def generate_code(self, prompt: str) -> GeneratedCodeResponse:
        """Generate Python code from a natural language prompt."""
        pass
