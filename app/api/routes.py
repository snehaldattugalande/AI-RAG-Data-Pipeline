from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.pipeline.embedding_pipeline import EmbeddingPipelineError
from app.pipeline.etl import ExtractTransformLoadError
from app.services.upload import UploadService
from app.services.chat import ChatService, ChatServiceError
from app.services.rag import RAGSystem
from app.api.schemas import (
    UploadResponse,
    QueryRequest,
    ChatRequest,
    ChatResponse,
    RAGResponse,
    HealthResponse,
)
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix=settings.api_prefix)

upload_service: UploadService | None = None
rag_system: RAGSystem | None = None
chat_service: ChatService | None = None
upload_directory = Path(settings.persist_directory).parents[0] / "uploads"
upload_directory.mkdir(parents=True, exist_ok=True)


def get_upload_service() -> UploadService:
    global upload_service
    if upload_service is None:
        upload_service = UploadService()
    return upload_service


def get_rag_system() -> RAGSystem:
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system


def get_chat_service() -> ChatService:
    global chat_service
    if chat_service is None:
        chat_service = ChatService()
    return chat_service

@router.post("/upload/pdf", response_model=UploadResponse, tags=["Upload"])
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    destination = upload_directory / file.filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = get_upload_service().process_pdf(destination)
        logger.info("Uploaded PDF: %s", file.filename)
        return result
    except (ExtractTransformLoadError, EmbeddingPipelineError, RuntimeError) as exc:
        logger.error("PDF upload failed for %s: %s", file.filename, exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.post("/upload/csv", response_model=UploadResponse, tags=["Upload"])
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    destination = upload_directory / file.filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = get_upload_service().process_csv(destination)
        logger.info("Uploaded CSV: %s", file.filename)
        return result
    except (ExtractTransformLoadError, EmbeddingPipelineError, RuntimeError) as exc:
        logger.error("CSV upload failed for %s: %s", file.filename, exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.post("/query", response_model=RAGResponse, tags=["RAG"])
async def query(request: QueryRequest):
    try:
        response = get_rag_system().answer(request.question)
        logger.info("Query executed: %s", request.question)
        return response
    except RuntimeError as exc:
        logger.error("Query failed: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    try:
        response = get_chat_service().chat(request.question, request.session_id or "default")
        sources = [
            {"metadata": doc.metadata, "content": doc.page_content}
            for doc in response.get("source_documents", [])
        ]
        return {
            "answer": response.get("answer"),
            "sources": sources,
            "session_id": request.session_id or "default",
        }
    except ChatServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "AI RAG Data Pipeline backend is healthy."}
