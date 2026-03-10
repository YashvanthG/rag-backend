from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import shutil
import os

from app.services.rag_service import (
    answer_question,
    list_documents,
    delete_by_source,
    delete_all_documents
)

from app.services.retrieval_service import test_retrieval
from app.services.document_service import upload_text
from app.services.file_service import extract_text_from_pdf

from app.models.schemas import (
    UploadRequest,
    UploadResponse,
    ChatRequest,
    DeleteRequest,
    RetrievalTestRequest
)

router = APIRouter()


# -------------------------
# Health Check
# -------------------------

@router.get("/health")
def health_check():
    return {"status": "Backend has started .."}


# -------------------------
# Upload Text
# -------------------------

@router.post("/upload", response_model=UploadResponse)
def upload(doc: UploadRequest):

    result = upload_text(doc.text)

    return UploadResponse(message=result)


# -------------------------
# Chat (Streaming)
# -------------------------

@router.post("/chat")
def chat(req: ChatRequest):

    try:

        generator = answer_question(
            question=req.question,
            history=req.history
        )

        return StreamingResponse(generator, media_type="text/plain")

    except Exception as e:

        print("CHAT ERROR:", e)

        def error_stream():
            yield "Server error."

        return StreamingResponse(error_stream(), media_type="text/plain")
    
# -------------------------
# Delete Specific Document
# -------------------------

@router.delete("/admin/delete")
def delete_document(req: DeleteRequest):

    return {"message": delete_by_source(req.source)}


# -------------------------
# Upload PDF
# -------------------------

@router.post("/admin/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):

    os.makedirs("temp", exist_ok=True)

    file_path = f"temp/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_path)

    result = upload_text(
        text=text,
        source=file.filename,
        category="pdf"
    )

    os.remove(file_path)

    return {"message": result}


# -------------------------
# List Documents
# -------------------------

@router.get("/admin/documents")
def get_documents():

    return list_documents()


# -------------------------
# Delete All Documents
# -------------------------

@router.delete("/admin/delete-all")
def delete_all():

    return {"message": delete_all_documents()}


# -------------------------
# Stats
# -------------------------

@router.get("/admin/stats")
def stats():

    docs = list_documents()

    total_chunks = sum(v["chunks"] for v in docs.values())

    return {
        "documents": len(docs),
        "chunks": total_chunks
    }


# -------------------------
# Retrieval Debug Endpoint
# -------------------------

@router.post("/admin/test-retrieval")
def retrieval_test(req: RetrievalTestRequest):

    results = test_retrieval(req.query)

    return {
        "query": req.query,
        "results": results
    }
