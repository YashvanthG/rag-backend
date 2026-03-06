from fastapi import FastAPI, Depends, HTTPException, Request
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
# Static Files
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
# Admin Authentication
# -------------------------------

def verify_admin(request: Request):
    admin_key = request.headers.get("X-Admin-Key") or request.query_params.get("key")

    if admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")


# -------------------------------
# Protected Swagger Docs
# -------------------------------

@app.get("/docs")
def get_docs(request: Request):
    verify_admin(request)

    key = request.query_params.get("key")

    openapi_url = "/openapi.json"
    if key:
        openapi_url = f"/openapi.json?key={key}"

    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API Docs"
    )


@app.get("/redoc")
def get_redoc(request: Request):
    verify_admin(request)

    key = request.query_params.get("key")

    openapi_url = "/openapi.json"
    if key:
        openapi_url = f"/openapi.json?key={key}"

    return get_redoc_html(
        openapi_url=openapi_url,
        title="ReDoc"
    )


@app.get("/openapi.json")
def openapi(request: Request):
    verify_admin(request)

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
# Protected Admin Dashboard
# -------------------------------

@app.get("/admin.html")
def serve_admin(request: Request):
    verify_admin(request)

    file_path = FRONTEND_DIR / "admin.html"

    if file_path.exists():
        return FileResponse(file_path)

    return {"message": "Admin UI not found"}
