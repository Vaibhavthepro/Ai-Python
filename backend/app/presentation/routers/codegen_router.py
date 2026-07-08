from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.infrastructure.ai.gemini_adapter import GeminiAIAdapter
from app.presentation.routers.auth_router import get_current_user

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    code: str
    explanation: str
    imports: List[str]

@router.post("/generate", response_model=GenerateResponse)
async def generate_code(req: GenerateRequest, current_user: dict = Depends(get_current_user)):
    adapter = GeminiAIAdapter()
    try:
        response = await adapter.generate_code(req.prompt)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
