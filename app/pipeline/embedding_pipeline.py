from pathlib import Path
from typing import Iterable, List

from app.core.logging import logger
from app.services.storage import VectorStore
from app.utils.file_parser import chunk_text


class EmbeddingPipelineError(Exception):
    pass


class EmbeddingPipeline:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self.vector_store = VectorStore()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, text: str) -> List[str]:
        if not text:
            logger.warning("Empty text provided for chunking")
            return []

        chunks = chunk_text(text, chunk_size=self.chunk_size, overlap=self.chunk_overlap)
        logger.debug("Chunked document into %d segments", len(chunks))
        return chunks

    def build_embeddings(self, texts: Iterable[str]) -> List[List[float]]:
        try:
            embedding_client = self.vector_store.embedding_client
            embeddings = embedding_client.embed_documents(list(texts))
            logger.info("Created embeddings for %d text segments", len(embeddings))
            return embeddings
        except Exception as exc:
            logger.exception("Failed to build embeddings")
            raise EmbeddingPipelineError("Embedding generation failed") from exc

    def prepare_documents(self, text: str, source: str) -> tuple[list[str], list[dict]]:
        chunks = self.chunk_document(text)
        metadatas = [{"source": source, "chunk_id": idx + 1} for idx in range(len(chunks))]
        return chunks, metadatas

    def index_documents(self, texts: Iterable[str], metadatas: Iterable[dict], incremental: bool = True):
        try:
            text_list = list(texts)
            metadata_list = list(metadatas)
            self.vector_store.add_documents(text_list, metadata_list)
            logger.info(
                "%s indexed %d documents",
                "Incrementally" if incremental else "Batch",
                len(text_list),
            )
        except Exception as exc:
            logger.exception("Failed to store documents in vector store")
            raise EmbeddingPipelineError("Failed to index documents") from exc

    def ingest_text(self, text: str, source: str, incremental: bool = True):
        if not text or not text.strip():
            raise EmbeddingPipelineError("No text provided for embedding ingestion.")

        texts, metadata = self.prepare_documents(text, source)
        if not texts:
            raise EmbeddingPipelineError("Document chunking produced no valid text segments.")

        self.index_documents(texts, metadata, incremental=incremental)
        return {"source": source, "chunks_added": len(texts), "incremental": incremental}

    def ingest_processed_file(self, file_path: Path, source: str | None = None, incremental: bool = True):
        try:
            raw_text = file_path.read_text(encoding="utf-8")
            source_name = source or file_path.stem
            return self.ingest_text(raw_text, source_name, incremental=incremental)
        except Exception as exc:
            logger.exception("Failed to ingest processed file %s", file_path)
            raise EmbeddingPipelineError("Processed file ingestion failed") from exc
