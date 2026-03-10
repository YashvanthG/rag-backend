from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    text: str


class UploadResponse(BaseModel):
    message: str



class ChatRequest(BaseModel):
    question: str
    history: list = Field(default_factory=list)

class ChatResponse(BaseModel):
    answer: str


class DeleteRequest(BaseModel):
    source: str

class RetrievalTestRequest(BaseModel):
    query: str
