from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.presentation.routers import auth_router, codegen_router, execution_router, snippet_router

app = FastAPI(title=settings.PROJECT_NAME)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(codegen_router.router, prefix=f"{settings.API_V1_STR}/codegen", tags=["Code Generation"])
app.include_router(execution_router.router, prefix=f"{settings.API_V1_STR}/execute", tags=["Execution"])
app.include_router(snippet_router.router, prefix=f"{settings.API_V1_STR}/snippets", tags=["Snippets"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
