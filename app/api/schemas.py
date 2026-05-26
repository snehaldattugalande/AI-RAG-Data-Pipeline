from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    source: str
    chunks_added: int
    processed_path: str


class QueryRequest(BaseModel):
    question: str = Field(..., title="Question", min_length=1)


class SourceDocument(BaseModel):
    metadata: Dict[str, Any]
    content: Optional[str] = None


class RAGResponse(BaseModel):
    answer: str
    sources: List[SourceDocument] = []


class ChatRequest(BaseModel):
    question: str = Field(..., title="Question", min_length=1)
    session_id: Optional[str] = Field("default", title="Session ID")


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument] = []
    session_id: str


class HealthResponse(BaseModel):
    status: str
    message: str
