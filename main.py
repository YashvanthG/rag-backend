from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from pathlib import Path

from app.api.routes import router
from app.core.config import settings


app = FastAPI(
    title="LPU RAG Assistant",
    description="AI assistant powered by RAG for university information",
    version="1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


# -------------------------------
# CORS
# -------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Include API Routes
# -------------------------------

app.include_router(router)


# -------------------------------
# Paths
# -------------------------------

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


# -------------------------------
# Static Files (if frontend exists)
# -------------------------------

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# -------------------------------
# Root Health Endpoint
# -------------------------------

@app.get("/")
def root():
    return {"message": "RAG backend running"}


# -------------------------------
# Admin Auth
# -------------------------------

def verify_admin(x_admin_key: str = Header(None)):
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")


# -------------------------------
# Protected Docs
# -------------------------------

@app.get("/docs", dependencies=[Depends(verify_admin)])
def get_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/redoc", dependencies=[Depends(verify_admin)])
def get_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")


@app.get("/openapi.json", dependencies=[Depends(verify_admin)])
def openapi():
    return get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes
    )


# -------------------------------
# Frontend Chat UI
# -------------------------------

@app.get("/chat")
def serve_chat():
    file_path = FRONTEND_DIR / "chat.html"

    if file_path.exists():
        return FileResponse(file_path)

    return {"message": "Chat UI not found. Backend running successfully."}


# -------------------------------
# Admin Dashboard UI
# -------------------------------

@app.get("/admin.html")
def serve_admin():
    file_path = FRONTEND_DIR / "admin.html"

    if file_path.exists():
        return FileResponse(file_path)

    return {"message": "Admin UI not found."}
