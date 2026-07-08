from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class User(BaseModel):
    id: UUID
    email: str
    role: str = "user"
    created_at: datetime

class CodeSnippet(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    prompt: Optional[str] = None
    storage_key: str
    language: str = "python"
    created_at: datetime
    updated_at: datetime

class ExecutionResult(BaseModel):
    job_id: str
    exit_code: int
    output: str
    duration_ms: Optional[int] = None
