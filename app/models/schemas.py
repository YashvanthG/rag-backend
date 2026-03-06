from pydantic import BaseModel


class UploadRequest(BaseModel):
    text: str


class UploadResponse(BaseModel):
    message: str


class ChatRequest(BaseModel):
    session_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str


class DeleteRequest(BaseModel):
    source: str

class RetrievalTestRequest(BaseModel):
    query: str
