from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
import uuid
from app.infrastructure.db.session import get_db
from app.infrastructure.db.models import CodeSnippetModel
from app.presentation.routers.auth_router import get_current_user
from app.infrastructure.storage.storage_factory import get_storage_service

router = APIRouter()

class SnippetCreate(BaseModel):
    title: str
    prompt: Optional[str]
    code: str
    language: str = "python"

class SnippetResponse(BaseModel):
    id: str
    title: str
    language: str

@router.post("/", response_model=SnippetResponse)
async def create_snippet(snippet: SnippetCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    storage = get_storage_service()
    key = f"{current_user['id']}/{uuid.uuid4()}.py"
    
    await storage.save(key, snippet.code.encode('utf-8'))
    
    db_snippet = CodeSnippetModel(
        user_id=current_user['id'],
        title=snippet.title,
        prompt=snippet.prompt,
        storage_key=key,
        language=snippet.language
    )
    db.add(db_snippet)
    await db.commit()
    await db.refresh(db_snippet)
    
    return {"id": str(db_snippet.id), "title": db_snippet.title, "language": db_snippet.language}

@router.get("/", response_model=List[SnippetResponse])
async def list_snippets(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(CodeSnippetModel).where(CodeSnippetModel.user_id == current_user['id'])
    result = await db.execute(stmt)
    snippets = result.scalars().all()
    return [{"id": str(s.id), "title": s.title, "language": s.language} for s in snippets]

@router.get("/{snippet_id}")
async def get_snippet(snippet_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(CodeSnippetModel).where(CodeSnippetModel.id == snippet_id, CodeSnippetModel.user_id == current_user['id'])
    result = await db.execute(stmt)
    snippet = result.scalar_one_or_none()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    storage = get_storage_service()
    code_bytes = await storage.read(snippet.storage_key)
    
    return {
        "id": str(snippet.id),
        "title": snippet.title,
        "prompt": snippet.prompt,
        "language": snippet.language,
        "code": code_bytes.decode('utf-8')
    }
