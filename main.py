from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.api.routes import router

app = FastAPI(
    title="LPU RAG Assistant",
    description="AI assistant powered by RAG for university information",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def root():
    return {"message": "RAG backend running"}

@app.get("/chat")
def serve_chat():
    return FileResponse(FRONTEND_DIR / "chat.html")

@app.get("/admin.html")
def serve_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")
