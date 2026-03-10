from pydantic import BaseModel


class UploadRequest(BaseModel):
    text: str


class UploadResponse(BaseModel):
    message: str


class ChatRequest(BaseModel):
    question: str
    history: list = []


class ChatResponse(BaseModel):
    answer: str


class DeleteRequest(BaseModel):
    source: str

class RetrievalTestRequest(BaseModel):
    query: str
