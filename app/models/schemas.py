from pydantic import BaseModel, Field
from typing import List, Literal


# -------------------------
# Upload
# -------------------------

class UploadRequest(BaseModel):
    text: str


class UploadResponse(BaseModel):
    message: str


# -------------------------
# Chat Models
# -------------------------

class Message(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        example="user"
    )
    content: str = Field(
        example="Tell me about LPU"
    )


class ChatRequest(BaseModel):
    question: str = Field(
        example="What is LPU?"
    )
    history: List[Message] = Field(
        default_factory=list
    )


class ChatResponse(BaseModel):
    answer: str


# -------------------------
# Admin Models
# -------------------------

class DeleteRequest(BaseModel):
    source: str


class RetrievalTestRequest(BaseModel):
    query: str